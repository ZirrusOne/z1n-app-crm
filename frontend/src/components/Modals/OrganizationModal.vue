<template>
  <Dialog v-model="show" :options="{ size: 'xl' }">
    <template #body>
      <div class="bg-surface-modal px-4 pb-6 pt-5 sm:px-6">
        <div class="mb-5 flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-semibold leading-6 text-ink-gray-9">
              {{ __('New Organization') }}
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
          :data="_organization"
          doctype="CRM Organization"
        />
=======
        <div>
          <div v-if="detailMode" class="flex flex-col gap-3.5">
            <div
              class="flex h-7 items-center gap-2 text-base text-gray-800"
              v-for="field in fields"
              :key="field.name"
            >
              <Tooltip :text="field.label">
                <div class="grid w-7 place-content-center">
                  <component :is="field.icon" />
                </div>
                <div>{{ field.value }}</div>
              </Tooltip>
            </div>
            <div
              class="flex h-7 items-center gap-2 text-base text-gray-800" v-if=" _organization.is_partner == 1">
              <Tooltip :text="'Partner'">
                <div class="grid w-7 place-content-center">
                  <PartnerIcon class="h-4 w-4" />
                </div>
                <div>Partner</div>
              </Tooltip>
            </div>
           
          </div>
   
          <Fields
            v-else-if="filteredSections"
            :sections="filteredSections"
            :data="_organization"
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
            @click="createOrganization"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import FieldLayout from '@/components/FieldLayout/FieldLayout.vue'
import EditIcon from '@/components/Icons/EditIcon.vue'
import { usersStore } from '@/stores/users'
<<<<<<< HEAD
import { isMobileView } from '@/composables/settings'
import { capture } from '@/telemetry'
import { call, FeatherIcon, createResource } from 'frappe-ui'
import { ref, nextTick, watch } from 'vue'
=======
import { customFormatNumberIntoCurrency } from '@/utils'
import { capture } from '@/telemetry'
import { call, FeatherIcon, Tooltip, createResource } from 'frappe-ui'
import { ref, nextTick, watch, computed, h } from 'vue'
>>>>>>> origin/Scrum-9-z1
import { useRouter } from 'vue-router'
import PartnerIcon from '@/components/Icons/PartnerIcon.vue'

const props = defineProps({
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
const organization = defineModel('organization')

const loading = ref(false)
const title = ref(null)

let _organization = ref({
  organization_name: '',
  website: '',
  annual_revenue: '',
  no_of_employees: '1-10',
  industry: '',
})

let doc = ref({})

<<<<<<< HEAD
async function createOrganization() {
=======
async function updateOrganization() {
  const old = { ...doc.value }
  const newOrg = { ..._organization.value }
  newOrg.annual_revenue = parseFloat(
    newOrg.annual_revenue.replace(/[^0-9.-]+/g, '')
        );

  const nameChanged = old.organization_name !== newOrg.organization_name
  delete old.organization_name
  delete newOrg.organization_name

  const otherFieldChanged = JSON.stringify(old) !== JSON.stringify(newOrg)
  const values = newOrg

  if (!nameChanged && !otherFieldChanged) {
    show.value = false
    return
  }

  let name
  loading.value = true
  if (nameChanged) {
    name = await callRenameDoc()
  }
  if (otherFieldChanged) {
    name = await callSetValue(values)
  }
  handleOrganizationUpdate({ name }, nameChanged)
}

async function callRenameDoc() {
  const d = await call('frappe.client.rename_doc', {
    doctype: 'CRM Organization',
    old_name: doc.value?.organization_name,
    new_name: _organization.value.organization_name,
  })
  loading.value = false
  return d
}

async function callSetValue(values) {
  const d = await call('frappe.client.set_value', {
    doctype: 'CRM Organization',
    name: _organization.value.name,
    fieldname: values,
  })
  loading.value = false
  return d.name
}

async function callInsertDoc() {
>>>>>>> origin/Scrum-9-z1
  const doc = await call('frappe.client.insert', {
    doc: {
      doctype: 'CRM Organization',
      ..._organization.value,
    },
  })
  loading.value = false
  if (doc.name) {
    capture('organization_created')
    handleOrganizationUpdate(doc)
  }
}

function handleOrganizationUpdate(doc) {
  if (doc.name && props.options.redirect) {
    router.push({
      name: 'Organization',
      params: { organizationId: doc.name },
    })
  } else {
    organization.value?.reload?.()
  }
  show.value = false
  props.options.afterInsert && props.options.afterInsert(doc)
}

<<<<<<< HEAD
const tabs = createResource({
=======
const dialogOptions = computed(() => {
  let title = !editMode.value
    ? __('New Organization')
    : __(_organization.value.organization_name)
  let size = detailMode.value ? '' : 'xl'
  let actions = detailMode.value
    ? []
    : [
        {
          label: editMode.value ? __('Save') : __('Create'),
          variant: 'solid',
          onClick: () =>
            editMode.value ? updateOrganization() : callInsertDoc(),
        },
      ]

  return { title, size, actions }
})

const fields = computed(() => {
  let details = [
    {
      icon: OrganizationsIcon,
      name: 'organization_name',
      label: 'Organization',
      value: `${_organization.value.organization_name}${
        _organization.value.government_affiliation
          ? ` (${_organization.value.government_affiliation})`
          : ''
    }`,
    },
    {
      icon: WebsiteIcon,
      name: 'website',
      label: 'Website',
      value: _organization.value.website,
    },
    {
      icon: TerritoryIcon,
      name: 'territory',
      label: 'Territory',
      value: _organization.value.territory,
    },
    {
      icon: MoneyIcon,
      name: 'annual_revenue',
      label: 'Amount',
      value: customFormatNumberIntoCurrency(
        _organization.value.annual_revenue,
        _organization.value.currency,
      ),
    },
    {
      icon: h(FeatherIcon, { name: 'hash', class: 'h-4 w-4' }),
      name: 'no_of_employees',
      label: 'Employees',
      value: _organization.value.no_of_employees,
    },
    {
      icon: h(FeatherIcon, { name: 'briefcase', class: 'h-4 w-4' }),
      name: 'industry',
      label: 'Industry',
      value: _organization.value.industry,
    },
  ]

  return details.filter((field) => field.value)
})

const sections = createResource({
>>>>>>> origin/Scrum-9-z1
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  cache: ['QuickEntry', 'CRM Organization'],
  params: { doctype: 'CRM Organization', type: 'Quick Entry' },
  auto: true,
  transform: (_tabs) => {
    return _tabs.forEach((tab) => {
      tab.sections.forEach((section) => {
        section.columns.forEach((column) => {
          column.fields.forEach((field) => {
            if (field.fieldname == 'address') {
              field.create = (value, close) => {
                _organization.value.address = value
                emit('openAddressModal')
                show.value = false
                close()
              }
              field.edit = (address) => {
                emit('openAddressModal', address)
                show.value = false
              }
            } else if (field.fieldtype === 'Table') {
              _organization.value[field.fieldname] = []
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
      // TODO: Issue with FormControl
      // title.value.el.focus()
      doc.value = organization.value?.doc || organization.value || {}
<<<<<<< HEAD
      _organization.value = { ...doc.value }
=======
    _organization.value = { 
            ...doc.value, 
            annual_revenue: doc.value.annual_revenue.toLocaleString('en-US', {
            style: 'currency',
            currency: doc.value.currency || 'USD',
        }) 
    };     
    if (_organization.value.name) {
        editMode.value = true
      }
>>>>>>> origin/Scrum-9-z1
    })
  },
)

const showQuickEntryModal = defineModel('showQuickEntryModal')

function openQuickEntryModal() {
  showQuickEntryModal.value = true
  nextTick(() => (show.value = false))
}

</script>
