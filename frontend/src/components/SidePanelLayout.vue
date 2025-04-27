<template>
  <div class="sections flex flex-col overflow-y-auto">
    <template v-for="(section, i) in _sections" :key="section.name">
      <div v-if="section.visible" class="section flex flex-col">
        <div
          v-if="i !== firstVisibleIndex()"
          class="w-full section-border h-px border-t"
        />
        <div class="p-1 sm:p-3">
          <Section
            labelClass="px-2 font-semibold"
            headerClass="h-8"
            :label="section.label"
            :hideLabel="!section.label"
            :opened="section.opened"
          >
            <template v-if="!preview" #actions>
              <slot name="actions" v-bind="{ section }">
                <Button
                  v-if="section.showEditButton"
                  variant="ghost"
                  class="w-7 mr-2"
                  @click="showSidePanelModal = true"
                >
                  <EditIcon class="h-4 w-4" />
                </Button>
              </slot>
            </template>
            <slot v-bind="{ section }">
              <FadedScrollableDiv
                v-if="section.columns?.[0].fields.length"
                class="column flex flex-col gap-1.5 overflow-y-auto"
              >
                <template
                  v-for="field in section.columns[0].fields || []"
                  :key="field.fieldname"
                >
                  <div
                    v-if="field.visible"
                    class="field flex items-center gap-2 px-3 leading-5 first:mt-3"
                  >
                    <Tooltip :text="__(field.label)" :hoverDelay="1">
                      <div
                        class="w-[35%] min-w-20 shrink-0 truncate text-sm text-ink-gray-5"
                      >
                        {{ __(field.label) }}
                        <span
                          v-if="
                            field.reqd ||
                            (field.mandatory_depends_on &&
                              field.mandatory_via_depends_on)
                          "
                          class="text-ink-red-3"
                          >*</span
                        >
                      </div>
                    </Tooltip>
                    <div class="flex items-center justify-between w-[65%]">
                      <div
                        class="grid min-h-[28px] flex-1 items-center overflow-hidden text-base"
                      >
                        <div
                          v-if="
                            field.read_only &&
                            !['Check', 'Dropdown'].includes(field.fieldtype)
                          "
                          class="flex h-7 cursor-pointer items-center px-2 py-1 text-ink-gray-5"
                        >
                          <Tooltip :text="__(field.tooltip)">
                            <div>{{ data[field.fieldname] }}</div>
                          </Tooltip>
                        </div>
                        <div v-else-if="field.fieldtype === 'Table MultiSelect'" class="form-control">
                          <!-- Display selected items as tags -->
                          <div v-if="Array.isArray(data[field.fieldname]) && data[field.fieldname].length" class="mb-2">
                            <div class="flex flex-wrap gap-1">
                              <div
                                v-for="item in data[field.fieldname]"
                                :key="item.name"
                                class="inline-flex items-center gap-1 rounded-md bg-surface-gray-3 px-2 py-1 text-xs"
                              >
                                {{ getTableMultiSelectItemLabel(field, item) }}
                                <span
                                  class="ml-1 cursor-pointer text-ink-gray-5 hover:text-ink-gray-9 font-medium"
                                  @click="removeTableMultiSelectItem(field, item)"
                                >
                                  ×
                                </span>
                              </div>
                            </div>
                          </div>

                          <!-- Dropdown to select new items -->
                          <div>
                            <NestedPopover>
                              <template #target="{ open }">
                                <Button
                                  variant="text"
                                  class="w-full min-h-7 justify-start border border-gray-100 bg-surface-gray-2 px-2 py-1 text-sm text-ink-gray-8 hover:border-outline-gray-modals hover:bg-surface-gray-3 focus:border-outline-gray-4"
                                >
                                  <div class="truncate">
                                    {{ __(getTableMultiSelectAddLabel(field)) }}
                                  </div>
                                  <template #suffix>
                                    <FeatherIcon
                                      :name="open ? 'chevron-up' : 'chevron-down'"
                                      class="h-4 text-ink-gray-5"
                                    />
                                  </template>
                                </Button>
                              </template>
                              <template #body>
                                <div class="p-2 min-w-52 max-h-64 overflow-y-auto space-y-1.5 divide-y divide-outline-gray-1 rounded-lg bg-surface-modal shadow-2xl ring-1 ring-black ring-opacity-5 focus:outline-none">
                                  <!-- Search box -->
                                  <div class="mb-2">
                                    <FormControl
                                      type="text"
                                      class="w-full"
                                      placeholder="Search..."
                                      v-model="tableMultiSelectSearchText[field.fieldname]"
                                    />
                                  </div>

                                  <!-- Options list -->
                                  <div v-if="getTableMultiSelectOptions(field).length" class="max-h-48 overflow-y-auto">
                                    <Button
                                      v-for="option in getTableMultiSelectOptions(field)"
                                      :key="option.value"
                                      variant="ghost"
                                      class="w-full !justify-start py-1.5 text-left"
                                      @click="addTableMultiSelectItem(field, option)"
                                    >
                                      {{ option.label }}
                                    </Button>
                                  </div>

                                  <div v-else class="py-2 text-center text-ink-gray-5 text-sm">
                                    {{ __('No options available') }}
                                  </div>
                                </div>
                              </template>
                            </NestedPopover>
                          </div>
                        </div>
                        <div v-else-if="field.fieldtype === 'Dropdown'">
                          <NestedPopover>
                            <template #target="{ open }">
                              <Button
                                :label="data[field.fieldname]"
                                class="dropdown-button flex w-full items-center justify-between rounded border border-gray-100 bg-surface-gray-2 px-2 py-1.5 text-base text-ink-gray-8 placeholder-ink-gray-4 transition-colors hover:border-outline-gray-modals hover:bg-surface-gray-3 focus:border-outline-gray-4 focus:bg-surface-white focus:shadow-sm focus:outline-none focus:ring-0 focus-visible:ring-2 focus-visible:ring-outline-gray-3"
                              >
                                <div
                                  v-if="data[field.fieldname]"
                                  class="truncate"
                                >
                                  {{ data[field.fieldname] }}
                                </div>
                                <div
                                  v-else
                                  class="text-base leading-5 text-ink-gray-4 truncate"
                                >
                                  {{ field.placeholder }}
                                </div>
                                <template #suffix>
                                  <FeatherIcon
                                    :name="open ? 'chevron-up' : 'chevron-down'"
                                    class="h-4 text-ink-gray-5"
                                  />
                                </template>
                              </Button>
                            </template>
                            <template #body>
                              <div
                                class="my-2 p-1.5 min-w-40 space-y-1.5 divide-y divide-outline-gray-1 rounded-lg bg-surface-modal shadow-2xl ring-1 ring-black ring-opacity-5 focus:outline-none"
                              >
                                <div>
                                  <DropdownItem
                                    v-if="field.options?.length"
                                    v-for="option in field.options"
                                    :key="option.name"
                                    :option="option"
                                  />
                                  <div v-else>
                                    <div
                                      class="p-1.5 px-7 text-base text-ink-gray-4"
                                    >
                                      {{
                                        __('No {0} Available', [field.label])
                                      }}
                                    </div>
                                  </div>
                                </div>
                                <div class="pt-1.5">
                                  <Button
                                    variant="ghost"
                                    class="w-full !justify-start"
                                    :label="__('Create New')"
                                    @click="field.create()"
                                  >
                                    <template #prefix>
                                      <FeatherIcon name="plus" class="h-4" />
                                    </template>
                                  </Button>
                                </div>
                              </div>
                            </template>
                          </NestedPopover>
                        </div>
                        <FormControl
                          v-else-if="field.fieldtype == 'Check'"
                          class="form-control"
                          type="checkbox"
                          v-model="data[field.fieldname]"
                          @change.stop="
                            emit(
                              'update',
                              field.fieldname,
                              $event.target.checked,
                            )
                          "
                          :disabled="Boolean(field.read_only)"
                        />
                        <FormControl
                          v-else-if="
                            [
                              'Small Text',
                              'Text',
                              'Long Text',
                              'Code',
                            ].includes(field.fieldtype)
                          "
                          class="form-control"
                          type="textarea"
                          :value="data[field.fieldname]"
                          :placeholder="field.placeholder"
                          :debounce="500"
                          @change.stop="
                            emit('update', field.fieldname, $event.target.value)
                          "
                        />
                        <FormControl
                          v-else-if="field.fieldtype === 'Select'"
                          class="form-control cursor-pointer [&_select]:cursor-pointer truncate"
                          type="select"
                          v-model="data[field.fieldname]"
                          :options="field.options"
                          :placeholder="field.placeholder"
                          @change.stop="
                            emit('update', field.fieldname, $event.target.value)
                          "
                        />
                        <Link
                          v-else-if="field.fieldtype === 'User'"
                          class="form-control"
                          :value="
                            data[field.fieldname] &&
                            getUser(data[field.fieldname]).full_name
                          "
                          doctype="User"
                          :filters="field.filters"
                          @change="
                            (data) => emit('update', field.fieldname, data)
                          "
                          :placeholder="'Select' + ' ' + field.label + '...'"
                          :hideMe="true"
                        >
                          <template v-if="data[field.fieldname]" #prefix>
                            <UserAvatar
                              class="mr-1.5"
                              :user="data[field.fieldname]"
                              size="sm"
                            />
                          </template>
                          <template #item-prefix="{ option }">
                            <UserAvatar
                              class="mr-1.5"
                              :user="option.value"
                              size="sm"
                            />
                          </template>
                          <template #item-label="{ option }">
                            <Tooltip :text="option.value">
                              <div class="cursor-pointer">
                                {{ getUser(option.value).full_name }}
                              </div>
                            </Tooltip>
                          </template>
                        </Link>
                        <Link
                          v-else-if="
                            ['Link', 'Dynamic Link'].includes(field.fieldtype)
                          "
                          class="form-control select-text"
                          :value="data[field.fieldname]"
                          :doctype="
                            field.fieldtype == 'Link'
                              ? field.options
                              : data[field.options]
                          "
                          :filters="field.filters"
                          :placeholder="field.placeholder"
                          @change="
                            (data) => emit('update', field.fieldname, data)
                          "
                          :onCreate="field.create"
                        />
                        <div
                          v-else-if="field.fieldtype === 'Datetime'"
                          class="form-control"
                        >
                          <DateTimePicker
                            icon-left=""
                            :value="data[field.fieldname]"
                            :formatter="
                              (date) => getFormat(date, '', true, true)
                            "
                            :placeholder="field.placeholder"
                            placement="left-start"
                            @change="
                              (data) => emit('update', field.fieldname, data)
                            "
                          />
                        </div>
                        <div
                          v-else-if="field.fieldtype === 'Date'"
                          class="form-control"
                        >
                          <DatePicker
                            icon-left=""
                            :value="data[field.fieldname]"
                            :formatter="(date) => getFormat(date, '', true)"
                            :placeholder="field.placeholder"
                            placement="left-start"
                            @change="
                              (data) => emit('update', field.fieldname, data)
                            "
                          />
                        </div>
                        <FormControl
                          v-else-if="field.fieldtype === 'Percent'"
                          class="form-control"
                          type="text"
                          :value="getFormattedPercent(field.fieldname, data)"
                          :placeholder="field.placeholder"
                          :debounce="500"
                          @change.stop="
                            emit(
                              'update',
                              field.fieldname,
                              flt($event.target.value),
                            )
                          "
                        />
                        <FormControl
                          v-else-if="field.fieldtype === 'Int'"
                          class="form-control"
                          type="number"
                          v-model="data[field.fieldname]"
                          :placeholder="field.placeholder"
                          :debounce="500"
                          @change.stop="
                            emit('update', field.fieldname, $event.target.value)
                          "
                        />
                        <FormControl
                          v-else-if="field.fieldtype === 'Float'"
                          class="form-control"
                          type="text"
                          :value="getFormattedFloat(field.fieldname, data)"
                          :placeholder="field.placeholder"
                          :debounce="500"
                          @change.stop="
                            emit(
                              'update',
                              field.fieldname,
                              flt($event.target.value),
                            )
                          "
                        />
                        <FormControl
                          v-else-if="field.fieldtype === 'Currency'"
                          class="form-control"
                          type="text"
                          :value="getFormattedCurrency(field.fieldname, data)"
                          :placeholder="field.placeholder"
                          :debounce="500"
                          @change.stop="
                            emit(
                              'update',
                              field.fieldname,
                              flt($event.target.value),
                            )
                          "
                        />
                        <FormControl
                          v-else
                          class="form-control"
                          type="text"
                          :value="data[field.fieldname]"
                          :placeholder="field.placeholder"
                          :debounce="500"
                          @change.stop="
                            emit('update', field.fieldname, $event.target.value)
                          "
                        />
                      </div>
                      <div class="ml-1">
                        <ArrowUpRightIcon
                          v-if="
                            field.fieldtype === 'Link' &&
                            field.link &&
                            data[field.fieldname]
                          "
                          class="h-4 w-4 shrink-0 cursor-pointer text-ink-gray-5 hover:text-ink-gray-8"
                          @click.stop="field.link(data[field.fieldname])"
                        />
                        <EditIcon
                          v-if="
                            field.fieldtype === 'Link' &&
                            field.edit &&
                            data[field.fieldname]
                          "
                          class="size-3.5 shrink-0 cursor-pointer text-ink-gray-5 hover:text-ink-gray-8"
                          @click.stop="field.edit(data[field.fieldname])"
                        />
                      </div>
                    </div>
                  </div>
                </template>
              </FadedScrollableDiv>
            </slot>
          </Section>
        </div>
      </div>
    </template>
  </div>
  <SidePanelModal
    v-if="showSidePanelModal"
    v-model="showSidePanelModal"
    :doctype="doctype"
    @reload="() => emit('reload')"
  />
</template>

<script setup>
import Section from '@/components/Section.vue'
import NestedPopover from '@/components/NestedPopover.vue'
import DropdownItem from '@/components/DropdownItem.vue'
import FadedScrollableDiv from '@/components/FadedScrollableDiv.vue'
import ArrowUpRightIcon from '@/components/Icons/ArrowUpRightIcon.vue'
import EditIcon from '@/components/Icons/EditIcon.vue'
import Link from '@/components/Controls/Link.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import SidePanelModal from '@/components/Modals/SidePanelModal.vue'
import { getMeta } from '@/stores/meta'
import { usersStore } from '@/stores/users'
import { isMobileView } from '@/composables/settings'
import { getFormat, evaluateDependsOnValue } from '@/utils'
import { flt } from '@/utils/numberFormat.js'
import { Tooltip, DateTimePicker, DatePicker, createResource } from 'frappe-ui'
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps({
  sections: {
    type: Object,
  },
  doctype: {
    type: String,
    default: 'CRM Lead',
  },
  preview: {
    type: Boolean,
    default: false,
  },
  addContact: {
    type: Function,
  },
  tableMultiSelectConfig: {
    type: Object,
    default: () => ({})
  }
})

const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } =
  getMeta(props.doctype)
const { isManager, getUser } = usersStore()

const emit = defineEmits(['update', 'reload'])

const data = defineModel()
const showSidePanelModal = ref(false)

const tableMultiSelectLabelFields = ref({});
const tableMultiSelectSearchText = ref({})
const tableMultiSelectOptions = ref({})
const tableMultiSelectLoading = ref({})

const _sections = computed(() => {
  if (!props.sections?.length) return []
  let editButtonAdded = false
  return props.sections.map((section) => {
    if (section.columns?.length) {
      section.columns[0].fields = section.columns[0].fields.map((field) => {
        return parsedField(field)
      })
    }
    let _section = parsedSection(section, editButtonAdded)
    if (_section.showEditButton) {
      editButtonAdded = true
    }
    return _section
  })
})

function parsedField(field) {
  if (field.fieldtype == 'Select' && typeof field.options === 'string') {
    field.options = field.options.split('\n').map((option) => {
      return { label: option, value: option }
    })

    if (field.options[0].value !== '') {
      field.options.unshift({ label: '', value: '' })
    }
  }

  if (field.fieldtype === 'Link' && field.options === 'User') {
    field.options = field.options
    field.fieldtype = 'User'
  }

  let _field = {
    ...field,
    filters: field.link_filters && JSON.parse(field.link_filters),
    placeholder: field.placeholder || field.label,
    display_via_depends_on: evaluateDependsOnValue(
      field.depends_on,
      data.value,
    ),
    mandatory_via_depends_on: evaluateDependsOnValue(
      field.mandatory_depends_on,
      data.value,
    ),
  }

  _field.visible = isFieldVisible(_field)
  return _field
}

function parsedSection(section, editButtonAdded) {
  let isContactSection = section.name == 'contacts_section'
  section.showEditButton = !(
    isMobileView.value ||
    !isManager() ||
    isContactSection ||
    editButtonAdded
  )

  section.visible =
    isContactSection ||
    section.columns?.[0].fields.filter((f) => f.visible).length

  return section
}

function isFieldVisible(field) {
  if (props.preview) return true
  return (
    (field.fieldtype == 'Check' ||
      (field.read_only && data.value[field.fieldname]) ||
      !field.read_only) &&
    (!field.depends_on || field.display_via_depends_on) &&
    !field.hidden
  )
}

function firstVisibleIndex() {
  return _sections.value.findIndex((section) => section.visible)
}

function getTableMultiSelectItemLabel(field, item) {
  // Get the display field from config
  const displayField = props.tableMultiSelectConfig[field.fieldname]?.displayField || 'name';

  // Try the display field
  if (item[displayField]) {
    return item[displayField];
  }

  // Fallbacks in priority order
  return item.label || item.value || item.name || '[missing label]';
}

function loadTableMultiSelectOptions(field) {
  // Skip if already loaded
  if (tableMultiSelectOptions.value[field.fieldname]) return

  // Set loading state
  tableMultiSelectLoading.value[field.fieldname] = true

  // Get options source from config or use default
  const source = props.tableMultiSelectConfig[field.fieldname]?.source ||
                 field.fieldname.replace(/s$/, ''); // Try singular form as fallback

  // Get the fields to fetch based on config
  const labelField = props.tableMultiSelectConfig[field.fieldname]?.labelField || 'name';
  const valueField = props.tableMultiSelectConfig[field.fieldname]?.valueField || 'name';

  // Prepare fields list for API
  const fieldsList = ['name'];

  // Add label/value fields if they differ from 'name'
  if (labelField !== 'name' && !fieldsList.includes(labelField)) {
    fieldsList.push(labelField);
  }
  if (valueField !== 'name' && valueField !== labelField && !fieldsList.includes(valueField)) {
    fieldsList.push(valueField);
  }

  // Create resource to fetch options
  createResource({
    url: 'frappe.client.get_list',
    params: {
      doctype: source,
      fields: fieldsList,
      limit: 500  // Adjust limit as needed
    },
    auto: true,
    onSuccess: (data) => {

      // Transform data to options format
      tableMultiSelectOptions.value[field.fieldname] = data.map(item => {
        // For display purposes, use the item's labelField or fallback to name
        const displayLabel = labelField && item[labelField] ? item[labelField] : item.name;
        const value = valueField && item[valueField] ? item[valueField] : item.name;

        return {
          label: displayLabel,
          value: value,
          // Store the full item for reference if needed
          data: item
        };
      });

      tableMultiSelectLoading.value[field.fieldname] = false;
    },
    onError: (error) => {
      tableMultiSelectLoading.value[field.fieldname] = false;
      tableMultiSelectOptions.value[field.fieldname] = [];
    }
  });
}

// Get filtered options based on search text
function getTableMultiSelectOptions(field) {
  // Load options if not already loaded
  if (!tableMultiSelectOptions.value[field.fieldname]) {
    loadTableMultiSelectOptions(field)
    return []
  }

  const options = tableMultiSelectOptions.value[field.fieldname] || []
  const searchText = tableMultiSelectSearchText.value[field.fieldname] || ''

  // If no search text, return all options
  if (!searchText) return options

  // Filter options based on search text
  return options.filter(option =>
    option.label.toLowerCase().includes(searchText.toLowerCase())
  )
}

// Add an item to the Table MultiSelect field
function addTableMultiSelectItem(field, option) {
  // If field value is not an array, initialize it
  if (!Array.isArray(data.value[field.fieldname])) {
    data.value[field.fieldname] = [];
  }

  // Get configuration for this field
  const config = props.tableMultiSelectConfig[field.fieldname] || {};
  const displayField = config.displayField || 'name';

  // Extract the actual value we want to use
  const elementValue = option.value;

  // Check if item already exists
  const exists = data.value[field.fieldname].some(item => {
    // Compare using displayField if it exists
    if (item[displayField]) {
      return item[displayField] === elementValue;
    }
    // Fallback to name
    return item.name === elementValue;
  });

  if (!exists) {
    // Create new item
    const newItem = {
      // Using temporary name just for client-side tracking
      name: `temp-${Math.random().toString(36).substr(2, 9)}`
    };

    // Set the display field with the value
    newItem[displayField] = elementValue;

    // Add item to array
    data.value[field.fieldname].push(newItem);

    // Emit update event
    emit('update', field.fieldname, data.value[field.fieldname]);
  }

  // Clear search text
  tableMultiSelectSearchText.value[field.fieldname] = '';
}

// Remove an item from the Table MultiSelect field
function removeTableMultiSelectItem(field, item) {

  if (Array.isArray(data.value[field.fieldname])) {
    // Get configuration for this field
    const config = props.tableMultiSelectConfig[field.fieldname] || {};
    const displayField = config.displayField || 'name';

    // Remove the item from the array - use item.name for comparison which is reliable
    data.value[field.fieldname] = data.value[field.fieldname].filter(i => {
      const isDifferent = i.name !== item.name;

      return isDifferent;
    });

    // Emit update event
    emit('update', field.fieldname, data.value[field.fieldname]);
  }
}

// Get label for add button
function getTableMultiSelectAddLabel(field) {
  return props.tableMultiSelectConfig[field.fieldname]?.addButtonLabel ||
         `Add ${field.label || 'Item'}`
}

// Initialize options for visible Table MultiSelect fields
onMounted(() => {
  // Check all sections for Table MultiSelect fields
  if (props.sections) {
    props.sections.forEach(section => {
      if (section.columns?.[0]?.fields) {
        section.columns[0].fields.forEach(field => {
          if (field.fieldtype === 'Table MultiSelect') {
            // Initialize search text
            tableMultiSelectSearchText.value[field.fieldname] = ''

            // Load options
            loadTableMultiSelectOptions(field)
          }
        })
      }
    })
  }
})
</script>

<style scoped>
.form-control {
  margin: 2px;
}

:deep(.form-control input:not([type='checkbox'])),
:deep(.form-control select),
:deep(.form-control textarea),
:deep(.form-control button),
.dropdown-button {
  border-color: transparent;
  background: transparent;
}

:deep(.form-control button) {
  gap: 0;
}
:deep(.form-control [type='checkbox']) {
  margin-left: 9px;
  cursor: pointer;
}

:deep(.form-control button > div) {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.form-control button svg) {
  color: white;
  width: 0;
}

.sections .section .column {
  max-height: 300px;
}
.sections .section:last-of-type .column {
  max-height: none;
}
</style>