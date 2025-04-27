<template>
  <Dialog v-model="show" :options="{ size: '3xl' }">
    <template #body>
      <div class="bg-white px-4 pb-6 pt-5 sm:px-6">
        <div class="mb-5 flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-semibold leading-6 text-gray-900">
              {{ __('Create Campaign') }}
            </h3>
          </div>
          <div class="flex items-center gap-1">
            <Button
              v-if="isManager()"
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
        
        <!-- Debug Information Section -->
        <div class="mb-4 p-2 bg-gray-100 rounded">
          <button @click="debug = !debug" class="text-xs text-blue-500 mb-2">
            {{ debug ? 'Hide Debug Info' : 'Show Debug Info' }}
          </button>
          
          <div v-if="debug">
            <div class="text-xs">
              <div><strong>Loading:</strong> {{ sections.loading }}</div>
              <div><strong>Error:</strong> {{ sections.error }}</div>
              <div><strong>Sections Count:</strong> {{ sections.data ? sections.data.length : 0 }}</div>
              <div><strong>Campaign Data:</strong></div>
              <pre class="overflow-auto max-h-40">{{ JSON.stringify(campaign, null, 2) }}</pre>
              
              <div class="mt-2"><strong>Sections Data:</strong></div>
              <pre class="overflow-auto max-h-40">{{ JSON.stringify(sections.data, null, 2) }}</pre>
              
              <div class="mt-2"><strong>Field Metadata:</strong></div>
              <pre class="overflow-auto max-h-40">{{ JSON.stringify(fieldMeta.data, null, 2) }}</pre>
            </div>
          </div>
        </div>
        
        <div>
          <div v-if="sections.loading || fieldMeta.loading" class="flex justify-center py-8">
            <div>{{ __('Loading fields...') }}</div>
          </div>
          <div v-else-if="sections.error" class="text-red-500">
            {{ __('Failed to load form fields') }}
          </div>
          <div v-else>
            <!-- Manual form creation based on the actual data structure -->
            <div v-for="(tab, tabIndex) in sections.data" :key="tabIndex">
              <div v-for="(section, sectionIndex) in tab.sections" :key="sectionIndex" class="mb-6">
                <div class="font-semibold mb-3">{{ section.label }}</div>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div v-for="fieldName in section.fields" :key="fieldName" class="mb-4">
                    <div class="mb-2 text-sm text-gray-600">
                      {{ getFieldLabel(fieldName) }}
                      <span class="text-red-500" v-if="isRequiredField(fieldName)">*</span>
                    </div>
                    
                    <!-- Different input types based on field name -->
                    <FormControl
                      v-if="getFieldType(fieldName) === 'Select'"
                      type="select"
                      :options="getFieldOptions(fieldName)"
                      v-model="campaign[fieldName]"
                      :placeholder="`Select ${getFieldLabel(fieldName)}`"
                    />
                    <DateTimePicker
                      v-else-if="fieldName === 'scheduled_send_time' && campaign.campaign_type === 'Email'"
                      v-model="campaign[fieldName]"
                      :placeholder="`Select ${getFieldLabel(fieldName)}`"
                      input-class="w-full p-2 border rounded"
                    />
                    <div v-else-if="fieldName === 'email_template' && campaign.campaign_type === 'Email'" class="flex gap-1">
                      <Link
                        class="form-control flex-1"
                        :value="campaign[fieldName]"
                        doctype="Email Template"
                        @change="(v) => (campaign[fieldName] = v)"
                        :placeholder="`Select ${getFieldLabel(fieldName)}`"
                      />
                    </div>
                    <FormControl
                      v-else
                      type="text"
                      v-model="campaign[fieldName]"
                      :placeholder="`Enter ${getFieldLabel(fieldName)}`"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="error" class="mt-4 text-sm text-red-500">
            {{ __(error) }}
          </div>
        </div>
      </div>
      <div class="px-4 pb-7 pt-4 sm:px-6">
        <div class="flex flex-row-reverse gap-2">
          <Button
            variant="solid"
            :label="__('Create')"
            :loading="isCampignCreating"
            @click="createCampign"
          />
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import EditIcon from '@/components/Icons/EditIcon.vue'
import { usersStore } from '@/stores/users'
import { capture } from '@/telemetry'
import { createResource } from 'frappe-ui'
import { ref, reactive, nextTick, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import Link from '@/components/Controls/Link.vue'
import { Button, Dialog, FeatherIcon, FormControl, DateTimePicker } from 'frappe-ui'

const props = defineProps({
  defaults: Object,
})

const { isManager } = usersStore()

const show = defineModel()
const router = useRouter()
const error = ref(null)
const debug = ref(false) // Default to false in production

// Initialize campaign with default values
const campaign = reactive({
  ...(props.defaults || {}),
  campaign_type: props.defaults?.campaign_type || 'Email',
  name: props.defaults?.name || '',
  status: props.defaults?.status || 'Draft',
  campaign_name: props.defaults?.campaign_name || '',
  scheduled_send_time: props.defaults?.scheduled_send_time || '',
  email_template: props.defaults?.email_template || '',
})

const isCampignCreating = ref(false)

// Fetch the doctype information to get field metadata
const fieldMeta = createResource({
  url: 'frappe.desk.form.load.getdoctype',
  params: {
    doctype: 'CRM Campaign',
    with_parent: 1
  },
  auto: true,
  onSuccess(data) {
    console.log('Fetched field metadata:', data)
  },
  onError(err) {
    console.error('Failed to load field metadata:', err)
  }
})

// Fallback options in case API fails
const fallbackOptions = {
  campaign_type: [
    { label: 'Email', value: 'Email' },
    { label: 'Call', value: 'Call' },
    { label: 'Meeting', value: 'Meeting' }
  ],
  status: [
    { label: 'Draft', value: 'Draft' },
    { label: 'Scheduled', value: 'Scheduled' },
    { label: 'In Progress', value: 'In Progress' },
    { label: 'Completed', value: 'Completed' },
    { label: 'Cancelled', value: 'Cancelled' }
  ]
}

// Helper function to get field options
function getFieldOptions(fieldName) {
  if (!fieldMeta.data || !fieldMeta.data.docs || !fieldMeta.data.docs[0]) {
    return fallbackOptions[fieldName] || []
  }
  
  const field = fieldMeta.data.docs[0].fields.find(f => f.fieldname === fieldName)
  
  if (!field || !field.options) {
    return fallbackOptions[fieldName] || []
  }
  
  // Parse options from the field
  return field.options.split('\n')
    .filter(opt => opt.trim())
    .map(opt => ({
      label: opt.trim(),
      value: opt.trim()
    }))
}

// Helper function to get field label
function getFieldLabel(fieldName) {
  if (!fieldMeta.data || !fieldMeta.data.docs || !fieldMeta.data.docs[0]) {
    return formatFieldLabel(fieldName)
  }
  
  const field = fieldMeta.data.docs[0].fields.find(f => f.fieldname === fieldName)
  
  if (!field || !field.label) {
    return formatFieldLabel(fieldName)
  }
  
  return field.label
}

// Helper function to get field type
function getFieldType(fieldName) {
  if (!fieldMeta.data || !fieldMeta.data.docs || !fieldMeta.data.docs[0]) {
    return 'Data' // Default type
  }
  
  const field = fieldMeta.data.docs[0].fields.find(f => f.fieldname === fieldName)
  
  if (!field || !field.fieldtype) {
    return 'Data' // Default type
  }
  
  return field.fieldtype
}

// Helper function to format field names into labels (as fallback)
function formatFieldLabel(fieldName) {
  // Convert snake_case to Title Case
  return fieldName
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

// Function to determine if a field is required
function isRequiredField(fieldName) {
  if (!fieldMeta.data || !fieldMeta.data.docs || !fieldMeta.data.docs[0]) {
    // Fallback for required fields
    return ['campaign_name', 'campaign_type', 'status'].includes(fieldName)
  }
  
  const field = fieldMeta.data.docs[0].fields.find(f => f.fieldname === fieldName)
  
  if (!field) {
    return ['campaign_name', 'campaign_type', 'status'].includes(fieldName)
  }
  
  return field.reqd === 1
}

// Log when component mounts
onMounted(() => {
  console.log('CampaignModal mounted')
  console.log('Initial campaign data:', JSON.parse(JSON.stringify(campaign)))
})

const sections = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_fields_layout',
  cache: ['quickEntryFields', 'CRM Campaign'],
  params: { doctype: 'CRM Campaign', type: 'Quick Entry' },
  auto: true,
  onSuccess(data) {
    console.log('Fetched sections data:', data)
    
    // Initialize any missing fields in the campaign object
    if (data && Array.isArray(data)) {
      data.forEach(tab => {
        if (tab.sections && Array.isArray(tab.sections)) {
          tab.sections.forEach(section => {
            if (section.fields && Array.isArray(section.fields)) {
              section.fields.forEach(fieldName => {
                if (campaign[fieldName] === undefined) {
                  campaign[fieldName] = ''
                }
              })
            }
          })
        }
      })
    }
  },
  onError(err) {
    console.error('Failed to load fields:', err)
    error.value = `Failed to load form fields: ${err.message || JSON.stringify(err)}`
  }
})

// Watch for changes to campaign fields to update dependencies
watch(() => campaign.campaign_type, (newType, oldType) => {
  console.log('Campaign type changed from', oldType, 'to', newType)
})

function validateCampaign() {
  const missingFields = []
  
  // Get fields to validate
  const fieldsToValidate = fieldMeta.data && fieldMeta.data.docs && fieldMeta.data.docs[0]
    ? fieldMeta.data.docs[0].fields.filter(f => f.reqd === 1).map(f => f.fieldname)
    : ['campaign_name', 'campaign_type', 'status']
  
  fieldsToValidate.forEach(field => {
    if (!campaign[field]) {
      missingFields.push(getFieldLabel(field))
    }
  })
  
  if (missingFields.length > 0) {
    error.value = `Please fill out required fields: ${missingFields.join(', ')}`
    return false
  }
  
  return true
}

function createCampign() {
  if (!validateCampaign()) {
    return
  }
  
  isCampignCreating.value = true
  error.value = null
  
  createResource({
    url: 'crm.fcrm.doctype.crm_campaign.crm_campaign.create_or_update_campaign',
    params: { args: campaign },
    auto: true,
    onSuccess(name) {
      capture('campign_created')
      isCampignCreating.value = false
      show.value = false
      router.push({ name: 'Campaign', params: { campaignId: name } })
    },
    onError(err) {
      isCampignCreating.value = false
      if (!err.messages) {
        error.value = err.message
        return
      }
      error.value = err.messages.join('\n')
    },
  })
}

const showQuickEntryModal = defineModel('quickEntry')

function openQuickEntryModal() {
  showQuickEntryModal.value = true
  nextTick(() => {
    show.value = false
  })
}
</script>

<style scoped>
/* Additional styling if needed */
</style>