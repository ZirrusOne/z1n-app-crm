<template>
  <div v-if="field.visible" class="field" :data-fieldname="field.fieldname">
    <div v-if="field.fieldtype != 'Check'" class="mb-2 text-sm text-ink-gray-5">
      {{ __(field.label) }}
      <span
        v-if="
          field.reqd ||
          (field.mandatory_depends_on && field.mandatory_via_depends_on)
        "
        class="text-ink-red-3"
        >*</span
      >
    </div>
    <FormControl
      v-if="field.read_only && field.fieldtype !== 'Check'"
      type="text"
      :placeholder="getPlaceholder(field)"
      v-model="data[field.fieldname]"
      :disabled="true"
    />
    <Grid
      v-else-if="field.fieldtype === 'Table'"
      v-model="data[field.fieldname]"
      :doctype="field.options"
      :parentDoctype="doctype"
    />
    <FormControl
      v-else-if="field.fieldtype === 'Select'"
      type="select"
      class="form-control"
      :class="field.prefix ? 'prefix' : ''"
      :options="field.options"
      v-model="data[field.fieldname]"
      :placeholder="getPlaceholder(field)"
    >
      <template v-if="field.prefix" #prefix>
        <IndicatorIcon :class="field.prefix" />
      </template>
    </FormControl>
    <div v-else-if="field.fieldtype == 'Check'" class="flex items-center gap-2">
      <FormControl
        class="form-control"
        type="checkbox"
        v-model="data[field.fieldname]"
        @change="(e) => (data[field.fieldname] = e.target.checked)"
        :disabled="Boolean(field.read_only)"
      />
      <label
        class="text-sm text-ink-gray-5"
        @click="
          () => {
            if (!Boolean(field.read_only)) {
              data[field.fieldname] = !data[field.fieldname]
            }
          }
        "
      >
        {{ __(field.label) }}
        <span class="text-ink-red-3" v-if="field.mandatory">*</span>
      </label>
    </div>
    <div
      class="flex gap-1"
      v-else-if="['Link', 'Dynamic Link'].includes(field.fieldtype)"
    >
      <Link
        class="form-control flex-1 truncate"
        :value="data[field.fieldname]"
        :doctype="
          field.fieldtype == 'Link' ? field.options : data[field.options]
        "
        :filters="field.filters"
        @change="(v) => (data[field.fieldname] = v)"
        :placeholder="getPlaceholder(field)"
        :onCreate="field.create"
      />
      <Button
        v-if="data[field.fieldname] && field.edit"
        class="shrink-0"
        :label="__('Edit')"
        @click="field.edit(data[field.fieldname])"
      >
        <template #prefix>
          <EditIcon class="h-4 w-4" />
        </template>
      </Button>
    </div>
    <div v-else-if="field.fieldtype === 'Table MultiSelect'" class="form-control relative">
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

      <!-- Custom dropdown trigger -->
      <Button
        variant="text"
        class="w-full min-h-7 justify-start border border-gray-100 bg-surface-gray-2 px-2 py-1 text-sm text-ink-gray-8 hover:border-outline-gray-modals hover:bg-surface-gray-3 focus:border-outline-gray-4"
        @click="toggleDropdown(field.fieldname)"
      >
        <div class="truncate">
          {{ __(getTableMultiSelectAddLabel(field)) }}
        </div>
        <template #suffix>
          <FeatherIcon
            :name="dropdownOpen[field.fieldname] ? 'chevron-up' : 'chevron-down'"
            class="h-4 text-ink-gray-5"
          />
        </template>
      </Button>

      <!-- Custom dropdown menu -->
      <div 
        v-if="dropdownOpen[field.fieldname]" 
        class="absolute left-0 right-0 mt-1 p-2 min-w-52 max-h-64 overflow-y-auto space-y-1.5 divide-y divide-outline-gray-1 rounded-lg bg-surface-modal shadow-2xl ring-1 ring-black ring-opacity-5 focus:outline-none z-50"
      >
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
            @click="selectAndCloseDropdown(field, option)"
          >
            {{ option.label }}
          </Button>
        </div>

        <div v-else class="py-2 text-center text-ink-gray-5 text-sm">
          {{ __('No options available') }}
        </div>
      </div>
    </div>
    <Link
      v-else-if="field.fieldtype === 'User'"
      class="form-control"
      :value="data[field.fieldname] && getUser(data[field.fieldname]).full_name"
      :doctype="field.options"
      :filters="field.filters"
      @change="(v) => (data[field.fieldname] = v)"
      :placeholder="getPlaceholder(field)"
      :hideMe="true"
    >
      <template #prefix>
        <UserAvatar
          v-if="data[field.fieldname]"
          class="mr-2"
          :user="data[field.fieldname]"
          size="sm"
        />
      </template>
      <template #item-prefix="{ option }">
        <UserAvatar class="mr-2" :user="option.value" size="sm" />
      </template>
      <template #item-label="{ option }">
        <Tooltip :text="option.value">
          <div class="cursor-pointer">
            {{ getUser(option.value).full_name }}
          </div>
        </Tooltip>
      </template>
    </Link>
    <DateTimePicker
      v-else-if="field.fieldtype === 'Datetime'"
      v-model="data[field.fieldname]"
      icon-left=""
      :formatter="(date) => getFormat(date, '', true, true)"
      :placeholder="getPlaceholder(field)"
      input-class="border-none"
    />
    <DatePicker
      v-else-if="field.fieldtype === 'Date'"
      icon-left=""
      v-model="data[field.fieldname]"
      :formatter="(date) => getFormat(date, '', true)"
      :placeholder="getPlaceholder(field)"
      input-class="border-none"
    />
    <FormControl
      v-else-if="
        ['Small Text', 'Text', 'Long Text', 'Code'].includes(field.fieldtype)
      "
      type="textarea"
      :placeholder="getPlaceholder(field)"
      v-model="data[field.fieldname]"
    />
    <FormControl
      v-else-if="['Int'].includes(field.fieldtype)"
      type="number"
      :placeholder="getPlaceholder(field)"
      v-model="data[field.fieldname]"
    />
    <FormControl
      v-else-if="field.fieldtype === 'Percent'"
      type="text"
      :value="getFormattedPercent(field.fieldname, data)"
      :placeholder="getPlaceholder(field)"
      :disabled="Boolean(field.read_only)"
      @change="data[field.fieldname] = flt($event.target.value)"
    />
    <FormControl
      v-else-if="field.fieldtype === 'Float'"
      type="text"
      :value="getFormattedFloat(field.fieldname, data)"
      :placeholder="getPlaceholder(field)"
      :disabled="Boolean(field.read_only)"
      @change="data[field.fieldname] = flt($event.target.value)"
    />
    <FormControl
      v-else-if="field.fieldtype === 'Currency'"
      type="text"
      :value="getFormattedCurrency(field.fieldname, data)"
      :placeholder="getPlaceholder(field)"
      :disabled="Boolean(field.read_only)"
      @change="data[field.fieldname] = flt($event.target.value)"
    />
    <FormControl
      v-else
      type="text"
      :placeholder="getPlaceholder(field)"
      v-model="data[field.fieldname]"
      :disabled="Boolean(field.read_only)"
    />
  </div>
</template>
<script setup>
import EditIcon from '@/components/Icons/EditIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import TableMultiselectInput from '@/components/Controls/TableMultiselectInput.vue'
import Link from '@/components/Controls/Link.vue'
import Grid from '@/components/Controls/Grid.vue'
import { getFormat, evaluateDependsOnValue } from '@/utils'
import { flt } from '@/utils/numberFormat.js'
import { getMeta } from '@/stores/meta'
import { usersStore } from '@/stores/users'
import { Tooltip, DatePicker, DateTimePicker, NestedPopover } from 'frappe-ui'
import { computed, inject, ref, onMounted, onUnmounted } from 'vue'
import { createResource } from 'frappe-ui'

const props = defineProps({
  field: Object,
  'data-name': String,
  tableMultiSelectConfig: {
    type: Object,
    default: () => ({})
  }
})

const data = inject('data')
const doctype = inject('doctype')
const preview = inject('preview')
// Try to get the tableMultiSelectConfig from injection first, then from props
const injectedTableMultiSelectConfig = inject('tableMultiSelectConfig', {})
const effectiveTableMultiSelectConfig = computed(() => props.tableMultiSelectConfig || injectedTableMultiSelectConfig)

const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } =
  getMeta(doctype)
const { getUser } = usersStore()

// Table MultiSelect related state
const tableMultiSelectSearchText = ref({})
const tableMultiSelectOptions = ref({})
const tableMultiSelectLoading = ref({})
const dropdownOpen = ref({})

// Field with parsing logic 
const field = computed(() => {
  let field = props.field
  if (field.fieldtype == 'Select' && typeof field.options === 'string') {
    field.options = field.options.split('\n').map((option) => {
      return { label: option, value: option }
    })

    if (field.options[0].value !== '') {
      field.options.unshift({ label: '', value: '' })
    }
  }

  if (field.fieldtype === 'Link' && field.options === 'User') {
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
})

function isFieldVisible(field) {
  if (preview.value) return true
  return (
    (field.fieldtype == 'Check' ||
      (field.read_only && data.value[field.fieldname]) ||
      !field.read_only) &&
    (!field.depends_on || field.display_via_depends_on) &&
    !field.hidden
  )
}

const getPlaceholder = (field) => {
  if (field.placeholder) {
    return __(field.placeholder)
  }
  if (['Select', 'Link'].includes(field.fieldtype)) {
    return __('Select {0}', [__(field.label)])
  } else {
    return __('Enter {0}', [__(field.label)])
  }
}

// Table MultiSelect methods
function getTableMultiSelectItemLabel(field, item) {
  // Get the display field from config
  const config = effectiveTableMultiSelectConfig.value[field.fieldname] || {}
  const displayField = config.displayField || 'name'

  // Try the display field
  if (item[displayField]) {
    return item[displayField]
  }

  // Fallbacks in priority order
  return item.label || item.value || item.name || '[missing label]'
}

function loadTableMultiSelectOptions(field) {
  // Skip if already loaded
  if (tableMultiSelectOptions.value[field.fieldname]) return

  // Set loading state
  tableMultiSelectLoading.value[field.fieldname] = true

  // Get config for this field
  const config = effectiveTableMultiSelectConfig.value[field.fieldname] || {}

  // Get options source from config or use default
  const source = config.source || 
                 field.options ||  // Try the field's options (doctype) first
                 field.fieldname.replace(/s$/, '') // Try singular form as fallback

  // Get the fields to fetch based on config
  const labelField = config.labelField || 'name'
  const valueField = config.valueField || 'name'

  // Prepare fields list for API
  const fieldsList = ['name']

  // Add label/value fields if they differ from 'name'
  if (labelField !== 'name' && !fieldsList.includes(labelField)) {
    fieldsList.push(labelField)
  }
  if (valueField !== 'name' && valueField !== labelField && !fieldsList.includes(valueField)) {
    fieldsList.push(valueField)
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
        const displayLabel = labelField && item[labelField] ? item[labelField] : item.name
        const value = valueField && item[valueField] ? item[valueField] : item.name

        return {
          label: displayLabel,
          value: value,
          // Store the full item for reference if needed
          data: item
        }
      })
      
      tableMultiSelectLoading.value[field.fieldname] = false
    },
    onError: (error) => {
      tableMultiSelectLoading.value[field.fieldname] = false
      tableMultiSelectOptions.value[field.fieldname] = []
    }
  })
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
    data.value[field.fieldname] = []
  }

  // Get configuration for this field
  const config = effectiveTableMultiSelectConfig.value[field.fieldname] || {}
  const displayField = config.displayField || 'name'

  // Extract the actual value we want to use
  const elementValue = option.value

  // Check if item already exists
  const exists = data.value[field.fieldname].some(item => {
    // Compare using displayField if it exists
    if (item[displayField]) {
      return item[displayField] === elementValue
    }
    // Fallback to name
    return item.name === elementValue
  })

  if (!exists) {
    // Create new item
    const newItem = {
      // Using temporary name just for client-side tracking
      name: `temp-${Math.random().toString(36).substr(2, 9)}`
    }

    // Set the display field with the value
    newItem[displayField] = elementValue

    // Add item to array
    data.value[field.fieldname].push(newItem)
  }

  // Clear search text
  tableMultiSelectSearchText.value[field.fieldname] = ''
}

// Remove an item from the Table MultiSelect field
function removeTableMultiSelectItem(field, item) {
  if (Array.isArray(data.value[field.fieldname])) {
    // Get configuration for this field
    const config = effectiveTableMultiSelectConfig.value[field.fieldname] || {}
    const displayField = config.displayField || 'name'

    // Remove the item from the array - use item.name for comparison which is reliable
    data.value[field.fieldname] = data.value[field.fieldname].filter(i => {
      return i.name !== item.name
    })
  }
}

// Get label for add button
function getTableMultiSelectAddLabel(field) {
  const config = effectiveTableMultiSelectConfig.value[field.fieldname] || {}
  return config.addButtonLabel || `Add ${field.label || 'Item'}`
}

function toggleDropdown(fieldname) {
  // Close all other dropdowns first
  Object.keys(dropdownOpen.value).forEach(key => {
    if (key !== fieldname) {
      dropdownOpen.value[key] = false
    }
  })
  
  // Toggle the current dropdown
  dropdownOpen.value[fieldname] = !dropdownOpen.value[fieldname]
}

function selectAndCloseDropdown(field, option) {
  addTableMultiSelectItem(field, option)
  dropdownOpen.value[field.fieldname] = false
}

// Close dropdown when clicking outside
function handleClickOutside(event) {
  const dropdownElements = document.querySelectorAll('.form-control.relative')
  
  dropdownElements.forEach(element => {
    if (!element.contains(event.target)) {
      const fieldname = element.dataset.fieldname
      if (fieldname && dropdownOpen.value[fieldname]) {
        dropdownOpen.value[fieldname] = false
      }
    }
  })
}

// Setup event listeners
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// Initialize table multi-select options for this field if needed
if (field.value.fieldtype === 'Table MultiSelect') {
  // Initialize search text
  tableMultiSelectSearchText.value[field.value.fieldname] = ''
  
  // Load options
  loadTableMultiSelectOptions(field.value)
}
</script>
<style scoped>
:deep(.form-control.prefix select) {
  padding-left: 2rem;
}

.table-multiselect-container {
  position: relative;
  display: flex;
  flex-direction: column;
}

.table-multiselect-container .selected-tags-container {
  position: relative;
  z-index: 20; /* Ensure tags stay above the dropdown */
}

.table-multiselect-container .dropdown-container {
  position: relative;
  z-index: 10;
}
</style>