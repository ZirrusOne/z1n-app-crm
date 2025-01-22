<template>
  <Dialog v-model="show" :options="{ size: 'xl' }">
    <template #body>
      <div class="bg-surface-modal px-4 pb-6 pt-5 sm:px-6">
        <div class="mb-5 flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-semibold leading-6 text-ink-gray-9">
              {{ __('New Contact') }}
            </h3>
          </div>
          <div class="flex items-center gap-1">
            <Button
              v-if="isManager() && !isMobileView"
              variant="ghost"
              class="w-7"
              @click="openQuickEntryModal"
            >
              <EditIcon class="h-4 w-4" />
            </Button>
            <Button variant="ghost" class="w-7" @click="show = false">
              <FeatherIcon name="x" class="h-4 w-4" />
            </Button>
          </div>
        </div>
<<<<<<< HEAD
        <FieldLayout
          v-if="tabs.data?.length"
          :tabs="tabs.data"
          :data="_contact"
          doctype="Contact"
        />
=======
        <div>
          <div v-if="detailMode" class="flex flex-col gap-3.5">
            <div
              v-for="field in detailFields"
              :key="field.name"
              class="flex h-7 items-center gap-2 text-base text-gray-800 crm-field-custom"
            >
              <Tooltip :text="field.label">
                <div class="grid w-7 place-content-center">
                  <component :is="field.icon" />
                </div>
              </Tooltip>
              <div v-if="field.type == 'dropdown'">
                <Dropdown
                  :options="field.options"
                  class="form-control -ml-2 mr-2 w-full flex-1"
                >
                  <template #default="{ open }">
                    <Button
                      variant="ghost"
                      :label="contact.data[field.name]"
                      class="dropdown-button w-full justify-between truncate hover:bg-white"
                    >
                      <div class="truncate">{{ contact.data[field.name] }}</div>
                      <template #suffix>
                        <FeatherIcon
                          :name="open ? 'chevron-up' : 'chevron-down'"
                          class="h-4 text-gray-600"
                        />
                      </template>
                    </Button>
                  </template>
                </Dropdown>
              </div>
              <div v-else>{{ field.value }}</div>
            </div>
          </div>
          <FieldsContacts
            v-else-if="filteredSections"
            :sections="filteredSections"
            :data="_contact"
          />
        </div>
>>>>>>> origin/Scrum-9-z1
      </div>
      <div class="px-4 pb-7 pt-4 sm:px-6">
        <div class="space-y-2">
          <Button
            class="w-full"
            variant="solid"
            :label="__('Create')"
            :loading="loading"
            @click="createContact"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
<<<<<<< HEAD
import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'
=======
import Fields from '@/components/Fields.vue'
import FieldsContacts from '@/components/FieldsContacts.vue'
import AddressModal from '@/components/Modals/AddressModal.vue'
import ContactIcon from '@/components/Icons/ContactIcon.vue'
import GenderIcon from '@/components/Icons/GenderIcon.vue'
import Email2Icon from '@/components/Icons/Email2Icon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import OrganizationsIcon from '@/components/Icons/OrganizationsIcon.vue'
import AddressIcon from '@/components/Icons/AddressIcon.vue'
import CertificateIcon from '@/components/Icons/CertificateIcon.vue'
>>>>>>> origin/Scrum-9-z1
import EditIcon from '@/components/Icons/EditIcon.vue'
import { usersStore } from '@/stores/users'
import { isMobileView } from '@/composables/settings'
import { capture } from '@/telemetry'
<<<<<<< HEAD
import { call, createResource } from 'frappe-ui'
import { ref, nextTick, watch } from 'vue'
=======
import { call, FeatherIcon, Tooltip, createResource } from 'frappe-ui'
import { ref, nextTick, watch, computed, h } from 'vue'
import { createToast } from '@/utils'
>>>>>>> origin/Scrum-9-z1
import { useRouter } from 'vue-router'

const props = defineProps({
  contact: {
    type: Object,
    default: {},
  },
  options: {
    type: Object,
    default: {
      redirect: true,
      afterInsert: () => {},
    },
  },
})

const emit = defineEmits(['openAddressModal'])

const { isManager } = usersStore()

const router = useRouter()
const show = defineModel()

const loading = ref(false)

let _contact = ref({})

async function createContact() {
  if (_contact.value.email_id) {
    _contact.value.email_ids = [{ email_id: _contact.value.email_id }]
    delete _contact.value.email_id
  }

  if (_contact.value.actual_mobile_no) {
    _contact.value.phone_nos = [{ phone: _contact.value.actual_mobile_no }]
    delete _contact.value.actual_mobile_no
  }
  

  const doc = await call('frappe.client.insert', {
    doc: {
      doctype: 'Contact',
      ..._contact.value,
    },
  })
  if (doc.name) {
    capture('contact_created')
    handleContactUpdate(doc)
  }
}

function handleContactUpdate(doc) {
  props.contact?.reload?.()
  if (doc.name && props.options.redirect) {
    router.push({
      name: 'Contact',
      params: { contactId: doc.name },
    })
  }
  show.value = false
  props.options.afterInsert && props.options.afterInsert(doc)
}

<<<<<<< HEAD
const tabs = createResource({
=======
const dialogOptions = computed(() => {
  let title = !editMode.value ? 'New Contact' : _contact.value.full_name

  let size = detailMode.value ? '' : 'xl'
  let actions = detailMode.value
    ? []
    : [
        {
          label: editMode.value ? 'Save' : 'Create',
          variant: 'solid',
          disabled: !dirty.value,
          onClick: () => (editMode.value ? updateContact() : callInsertDoc()),
        },
      ]

  return { title, size, actions }
})

const detailFields = computed(() => {
  let details = [
    {
      icon: ContactIcon,
      name: 'full_name',
      label: 'Full Name',
      value:
        (_contact.value.salutation ? _contact.value.salutation + '. ' : '') +
        _contact.value.full_name,
    },
    {
      icon: GenderIcon,
      name: 'gender',
      label: 'Gender',
      value: _contact.value.gender,
    },
    {
      icon: Email2Icon,
      name: 'email_id',
      label: 'Email',
      value: _contact.value.email_id,
    },
    {
      icon: h(FeatherIcon, { name: 'user', class: 'h-4 w-4' }), 
      name: 'custom_is_personal',
      label: 'Personal Contact', 
      value: _contact.value.custom_is_personal ? 'Yes' : 'No', 
    },
    {
      icon: PhoneIcon,
      name: 'mobile_no',
      label: 'Mobile No',
      value: _contact.value.actual_mobile_no,
    },
    {
      icon: OrganizationsIcon,
      name: 'company_name',
      label: 'Company Name',
      value: _contact.value.company_name,
    },
    {
      icon: CertificateIcon,
      name: 'designation',
      label: 'Job Title',
      value: _contact.value.designation,
    },
    {
      icon: h(FeatherIcon, { name: 'divide-square', class: 'h-4 w-4' }),
      name: 'custom_business_unit',
      label: 'Business Unit',
      value: _contact.value.custom_business_unit,
    },
    {
      icon: h(FeatherIcon, { name: 'dollar-sign', class: 'h-4 w-4' }),
      name: 'custom_buying_role',
      label: 'Buying Role',
      value: _contact.value.custom_buying_role,
    },
    {
      icon: AddressIcon,
      name: 'address',
      label: 'Address',
      value: _contact.value.address,
    },
  ]

  return details.filter((detail) => detail.value)
})

const sections = createResource({
>>>>>>> origin/Scrum-9-z1
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  cache: ['QuickEntry', 'Contact'],
  params: { doctype: 'Contact', type: 'Quick Entry' },
  auto: true,
<<<<<<< HEAD
  transform: (_tabs) => {
    return _tabs.forEach((tab) => {
      tab.sections.forEach((section) => {
        section.columns.forEach((column) => {
          column.fields.forEach((field) => {
            if (field.fieldname == 'email_id') {
              field.read_only = false
            } else if (field.fieldname == 'mobile_no') {
              field.read_only = false
            } else if (field.fieldname == 'address') {
              field.create = (value, close) => {
                _contact.value.address = value
                emit('openAddressModal')
                show.value = false
                close()
              }
              field.edit = (address) => {
                emit('openAddressModal', address)
                show.value = false
              }
            } else if (field.fieldtype === 'Table') {
              _contact.value[field.fieldname] = []
=======
})

const filteredSections = computed(() => {
  let allSections = sections.data || []
  if (!allSections.length) return []

  allSections.forEach((s) => {
    s.fields.forEach((field) => {
      if (field.name === 'custom_is_personal') {
        field.label = 'Personal Contact'; 
      }
      if (field.name == 'email_id') {
        field.type = props.contact?.data?.name ? 'Dropdown' : 'Data'
        field.options =
          props.contact.data?.email_ids?.map((email) => {
            return {
              name: email.name,
              value: email.email_id,
              selected: email.email_id === props.contact.data.email_id,
              placeholder: 'john@doe.com',
              onClick: () => {
                _contact.value.email_id = email.email_id
                setAsPrimary('email', email.email_id)
              },
              onSave: (option, isNew) => {
                if (isNew) {
                  createNew('email', option.value)
                  if (props.contact.data.email_ids.length === 1) {
                    _contact.value.email_id = option.value
                  }
                } else {
                  editOption('Contact Email', option.name, option.value)
                }
              },
              onDelete: async (option, isNew) => {
                props.contact.data.email_ids =
                  props.contact.data.email_ids.filter(
                    (email) => email.name !== option.name,
                  )
                !isNew && (await deleteOption('Contact Email', option.name))
                if (_contact.value.email_id === option.value) {
                  if (props.contact.data.email_ids.length === 0) {
                    _contact.value.email_id = ''
                  } else {
                    _contact.value.email_id = props.contact.data.email_ids.find(
                      (email) => email.is_primary,
                    )?.email_id
                  }
                }
              },
>>>>>>> origin/Scrum-9-z1
            }
          })
        })
      })
    })
  },
})

watch(
  () => show.value,
  (value) => {
    if (!value) return
    nextTick(() => {
      _contact.value = { ...props.contact.data }
    })
  },
)

const showQuickEntryModal = defineModel('showQuickEntryModal')

function openQuickEntryModal() {
  showQuickEntryModal.value = true
  nextTick(() => (show.value = false))
}
</script>

<style scoped>
:deep(:has(> .dropdown-button)) {
  width: 100%;
}
</style>
