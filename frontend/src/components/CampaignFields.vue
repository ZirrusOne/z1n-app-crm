<template>
  <div class="flex flex-col gap-4">
    <div
      v-for="section in sections"
      :key="section.label"
      class="section first:border-t-0 first:pt-0"
      :class="section.hideBorder ? '' : 'border-t pt-4'"
    >
      <div
        v-if="!section.hideLabel"
        class="flex h-7 mb-3 max-w-fit cursor-pointer items-center gap-2 text-base font-semibold leading-5"
      >
        {{ section.label }}
      </div>
      <div
        class="grid gap-4"
        :class="
          section.columns
            ? 'grid-cols-' + section.columns
            : 'grid-cols-2 sm:grid-cols-3'
        "
      >
        <div v-for="field in section.fields" :key="field.name">
          <div
            class="settings-field"
            v-if="
              (field.type == 'Check' ||
                (field.read_only && data[field.name]) ||
                !field.read_only ||
                !field.hidden) &&
              (!field.depends_on || field.display_via_depends_on)
            "
          >
            <div
              v-if="field.type != 'Check' && field.name !== 'scheduled_send_time' && field.name !=='email_template'"
              class="mb-2 text-sm text-gray-600"
            >
              {{ __(field.label) }}
              <span
                class="text-red-500"
                v-if="
                  field.mandatory ||
                  (field.mandatory_depends_on && field.mandatory_via_depends_on)
                "
                >*</span
              >
            </div>
            <div
              v-if="(field.name === 'scheduled_send_time' &&  data['campaign_type'] =='Email') || (field.name === 'email_template' &&  data['campaign_type'] =='Email') "
              class="mb-2 text-sm text-gray-600"
            >
              {{ __(field.label) }}
              <span
                class="text-red-500"
                v-if="
                  field.mandatory ||
                  (field.mandatory_depends_on && field.mandatory_via_depends_on)
                "
                >*</span
              >
            </div>
            <FormControl
              v-if="field.read_only && field.type !== 'Check'"
              type="text"
              :placeholder="getPlaceholder(field)"
              v-model="data[field.name]"
              :disabled="true"
            />
            <FormControl
              v-else-if="field.type === 'Select'"
              type="select"
              class="form-control"
              :class="field.prefix ? 'prefix' : ''"
              :options="field.options"
              v-model="data[field.name]"
              :placeholder="getPlaceholder(field)"
            >
              <template v-if="field.prefix" #prefix>
                <IndicatorIcon :class="field.prefix" />
              </template>
            </FormControl>
            <div
              v-else-if="field.type == 'Check'"
              class="flex items-center gap-2"
            >
              <FormControl
                class="form-control"
                type="checkbox"
                v-model="data[field.name]"
                @change="(e) => (data[field.name] = e.target.checked)"
                :disabled="Boolean(field.read_only)"
              />
              <label
                class="text-sm text-gray-600"
                @click="data[field.name] = !data[field.name]"
              >
                {{ __(field.label) }}
                <span class="text-red-500" v-if="field.mandatory">*</span>
              </label>
            </div>
            <div class="flex gap-1" v-else-if="field.type === 'Link' && field.name !== 'email_template'">
              <Link
                class="form-control flex-1"
                :value="data[field.name]"
                :doctype="field.options"
                :filters="field.filters"
                @change="(v) => (data[field.name] = v)"
                :placeholder="getPlaceholder(field)"
                :onCreate="field.create"
              />
              <Button
                v-if="data[field.name] && field.edit"
                class="shrink-0"
                :label="__('Edit')"
                @click="field.edit(data[field.name])"
              >
                <template #prefix>
                  <EditIcon class="h-4 w-4" />
                </template>
              </Button>
            </div>
            <div class="flex gap-1" v-else-if="field.type === 'Link' && field.name === 'email_template' && data['campaign_type'] =='Email'"  >
              <Link
                class="form-control flex-1"
                :value="data[field.name]"
                :doctype="field.options"
                :filters="field.filters"
                @change="(v) => (data[field.name] = v)"
                :placeholder="getPlaceholder(field)"
                :onCreate="field.create"
              />
              <Button
                v-if="data[field.name] && field.edit"
                class="shrink-0"
                :label="__('Edit')"
                @click="field.edit(data[field.name])"
              >
                <template #prefix>
                  <EditIcon class="h-4 w-4" />
                </template>
              </Button>
            </div>

            <Link
              v-else-if="field.type === 'User'"
              class="form-control"
              :value="getUser(data[field.name]).full_name"
              :doctype="field.options"
              :filters="field.filters"
              @change="(v) => (data[field.name] = v)"
              :placeholder="getPlaceholder(field)"
              :hideMe="true"
            >
              <template #prefix>
                <UserAvatar class="mr-2" :user="data[field.name]" size="sm" />
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
            <div v-else-if="field.type === 'Dropdown'">
              <NestedPopover>
                <template #target="{ open }">
                  <Button
                    :label="data[field.name]"
                    class="dropdown-button flex w-full items-center justify-between rounded border border-gray-100 bg-gray-100 px-2 py-1.5 text-base text-gray-800 placeholder-gray-500 transition-colors hover:border-gray-200 hover:bg-gray-200 focus:border-gray-500 focus:bg-white focus:shadow-sm focus:outline-none focus:ring-0 focus-visible:ring-2 focus-visible:ring-gray-400"
                  >
                    <div class="truncate">{{ data[field.name] }}</div>
                    <template #suffix>
                      <FeatherIcon
                        :name="open ? 'chevron-up' : 'chevron-down'"
                        class="h-4 text-gray-600"
                      />
                    </template>
                  </Button>
                </template>
                <template #body>
                  <div
                    class="my-2 space-y-1.5 divide-y rounded-lg border border-gray-100 bg-white p-1.5 shadow-xl"
                  >
                    <div>
                      <DropdownItem
                        v-if="field.options?.length"
                        v-for="option in field.options"
                        :key="option.name"
                        :option="option"
                      />
                      <div v-else>
                        <div class="p-1.5 px-7 text-base text-gray-500">
                          {{ __('No {0} Available', [field.label]) }}
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
            <DateTimePicker
              v-else-if="field.type === 'Datetime' &&  data['campaign_type'] =='Email'"
              v-model="data[field.name]"
              :placeholder="getPlaceholder(field)"
              input-class="border-none"
            />
            <DatePicker
              v-else-if="field.type === 'Date'"
              v-model="data[field.name]"
              :placeholder="getPlaceholder(field)"
              input-class="border-none"
            />
            <FormControl
              v-else-if="
                ['Small Text', 'Text', 'Long Text'].includes(field.type)
              "
              type="textarea"
              :placeholder="getPlaceholder(field)"
              v-model="data[field.name]"
            />
            <FormControl
              v-else-if="['Int'].includes(field.type)"
              type="number"
              :placeholder="getPlaceholder(field)"
              v-model="data[field.name]"
            />
            <FormControl
              v-else-if="field.type !== 'Datetime' && field.name !== 'email_template'"
              type="text"
              :placeholder="getPlaceholder(field)"
              v-model="data[field.name]"
              :disabled="Boolean(field.read_only)"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import EditIcon from '@/components/Icons/EditIcon.vue'
import NestedPopover from '@/components/NestedPopover.vue'
import DropdownItem from '@/components/DropdownItem.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import Link from '@/components/Controls/Link.vue'
import { usersStore } from '@/stores/users'
import { Tooltip, DatePicker, DateTimePicker } from 'frappe-ui'

const { getUser } = usersStore()

const props = defineProps({
  sections: Array,
  data: Object,
})

const getPlaceholder = (field) => {
  if (field.placeholder) {
    return __(field.placeholder)
  }
  if (['Select', 'Link'].includes(field.type)) {
    return __('Select {0}', [__(field.label)])
  } else {
    return __('Enter {0}', [__(field.label)])
  }
}
</script>

<style scoped>
:deep(.form-control.prefix select) {
  padding-left: 2rem;
}

.section {
  display: none;
}

.section:has(.settings-field) {
  display: block;
}
</style>