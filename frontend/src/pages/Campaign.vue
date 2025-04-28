<template>
  <LayoutHeader v-if="campaignData">
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs">
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
    </template>
  </LayoutHeader>

  <div v-if="campaignData" class="flex flex-1 flex-col overflow-hidden">
    <!-- Campaign title section -->
    <div class="flex items-start justify-start gap-6 p-5 sm:items-center">
      <div class="flex flex-col justify-center gap-2 sm:gap-0.5">
        <div class="text-3xl font-semibold text-gray-900">
          {{ campaignData.campaign_name || campaignData.name || 'Unnamed Campaign' }}
        </div>
        <div class="flex flex-col flex-wrap gap-3 text-base text-gray-700 sm:flex-row sm:items-center sm:gap-2">
        <!-- Email Template (only for Email campaigns) -->
        <template v-if="campaignData.campaign_type === 'Email' && campaignData.email_template">
          <Tooltip text="Email Template">
            <div class="flex items-center gap-1.5">
              <FeatherIcon name="mail" class="h-4 w-4" />
              <span>{{ campaignData.email_template }}</span>
            </div>
          </Tooltip>
          <span class="hidden text-3xl leading-[0] text-gray-600 sm:flex">
            &middot;
          </span>
        </template>

        <!-- Campaign Type -->
        <Tooltip text="Campaign Type" v-if="campaignData.campaign_type">
          <div class="flex items-center gap-1.5">
            <FeatherIcon name="tag" class="h-4 w-4" />
            <span>{{ campaignData.campaign_type }}</span>
          </div>
        </Tooltip>

        <!-- Separator -->
        <span v-if="campaignData.campaign_type && campaignData.status" class="hidden text-3xl leading-[0] text-gray-600 sm:flex">
          &middot;
        </span>

        <!-- Editable Status -->
        <Tooltip text="Status" v-if="campaignData.status">
          <div class="flex items-center gap-1.5 cursor-pointer" @click="startEditingStatus">
            <FeatherIcon name="bookmark" class="h-4 w-4" />
            <span v-if="!isEditingStatus">{{ campaignData.status }}</span>
            <div v-else class="relative">
              <select 
                v-model="editedStatus"
                class="min-w-32 border rounded p-1 text-base text-gray-700"
                @change="saveStatus"
                @blur="isEditingStatus = false"
                ref="statusSelect"
              >
                <option v-for="option in formattedStatusOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>
            <FeatherIcon v-if="!isEditingStatus" name="edit-2" class="h-3 w-3 ml-1 text-gray-500" />
          </div>
        </Tooltip>

        <!-- Scheduled Send Time -->
        <span v-if="campaignData.scheduled_send_time" class="hidden text-3xl leading-[0] text-gray-600 sm:flex">
          &middot;
        </span>
        <Tooltip text="Scheduled Time" v-if="campaignData.scheduled_send_time">
          <div class="flex items-center gap-1.5 cursor-pointer" @click="isEditingScheduledTime = true">
            <FeatherIcon name="calendar" class="h-4 w-4" />
            <span v-if="!isEditingScheduledTime">
              {{ formatDate(campaignData.scheduled_send_time, 'MMM D, YYYY h:mm A') }}
            </span>
            <DateTimePicker
              v-else
              v-model="editedScheduledTime"
              :dateFormat="'MMM d, yyyy h:mm aa'"
              :enableTimeSeconds="false"
              class="border rounded p-1"
              @update:modelValue="onScheduledTimeChange"
              autoApply
            />
            <FeatherIcon v-if="!isEditingScheduledTime" name="edit-2" class="h-3 w-3 ml-1 text-gray-500" />
          </div>
        </Tooltip>

        </div>
        <div class="flex flex-col flex-wrap gap-3 text-base text-gray-700 sm:flex-row sm:items-center sm:gap-2">
          <!-- Email Template (only for Email campaigns) -->
          <template v-if="campaignData.campaign_type === 'Email' && campaignData.email_template">
            <Tooltip text="Email Template">
              <div class="flex items-center gap-1.5">
                <FeatherIcon name="mail" class="h-4 w-4" />
                <span class="">{{ campaignData.email_template }}</span>
              </div>
            </Tooltip>
            <span class="hidden text-3xl leading-[0] text-gray-600 sm:flex">
              &middot;
            </span>
          </template>
          
          <!-- Campaign Type -->
          <Tooltip text="Campaign Type" v-if="campaignData.campaign_type">
            <div class="flex items-center gap-1.5">
              <FeatherIcon name="tag" class="h-4 w-4" />
              <span class="">{{ campaignData.campaign_type }}</span>
            </div>
          </Tooltip>

      </div>
    </div>

    <!-- Tabs section -->
    <Tabs as="div" v-model="tabIndex" :tabs="tabs">
      <template #tab-item="{ tab, selected }">
        <button
          class="group flex items-center gap-2 border-b border-transparent py-2.5 text-base text-gray-600 duration-300 ease-in-out hover:border-gray-400 hover:text-gray-900"
          :class="{ 'text-gray-900': selected }"
        >
          <component v-if="tab.icon" :is="tab.icon" class="h-5" />
          {{ __(tab.label) }}
          <Badge
            class="group-hover:bg-gray-100"
            :class="[selected ? 'bg-gray-100' : 'bg-gray-50']"
            variant="solid"
            theme="gray"
            size="sm"
          >
            {{ tab.count }}
          </Badge>
        </button>
      </template>
      <template #tab-panel="{ tab }">
        <div v-if="isLoadingParticipants" class="flex justify-center py-8">
          <div>{{ __('Loading data...') }}</div>
        </div>
        <LeadsListView
          class="mt-4"
          v-if="tab.label === 'Leads' && mappedLeadParticipants.length"
          :rows="mappedLeadParticipants"
          :columns="leadColumns"
          :options="{ selectable: false, showTooltip: true }"
        />
        <ContactsListView
          class="mt-4"
          v-if="tab.label === 'Contacts' && mappedContactParticipants.length"
          :rows="mappedContactParticipants"
          :columns="contactColumns"
          :options="{ selectable: false, showTooltip: true }"
        />
        <div
          v-if="(tab.label === 'Leads' && !mappedLeadParticipants.length) || 
               (tab.label === 'Contacts' && !mappedContactParticipants.length)"
          class="grid flex-1 place-items-center text-xl font-medium text-gray-500 mt-10"
        >
          <div class="flex flex-col items-center justify-center space-y-3">
            <component :is="tab.icon" class="!h-10 !w-10" />
            <div>{{ __('No {0} Found', [__(tab.label)]) }}</div>
          </div>
        </div>
      </template>
    </Tabs>
    
    <!-- Success Toast for Date Change -->
    <Toast
      v-if="showSaveSuccess"
      theme="success"
      :title="__('Update Successful')"
      :subtitle="__('Campaign details have been updated')"
      @hide="showSaveSuccess = false"
    />
  </div>
  
  <!-- Loading State -->
  <div v-else class="flex-1 grid place-items-center">
    <div class="flex flex-col items-center justify-center space-y-3">
      <FeatherIcon name="loader" class="h-10 w-10 animate-spin" />
      <div class="text-lg text-gray-600">{{ __('Loading Campaign...') }}</div>
    </div>
  </div>
  
  <!-- Loading State -->
  <div v-else class="flex-1 grid place-items-center">
    <div class="flex flex-col items-center justify-center space-y-3">
      <FeatherIcon name="loader" class="h-10 w-10 animate-spin" />
      <div class="text-lg text-gray-600">{{ __('Loading Campaign...') }}</div>
    </div>
  </div>
</template>

<script setup>
import LeadsListView from '@/components/ListViews/LeadsListView.vue'
import ContactsListView from '@/components/ListViews/ContactsListView.vue'
import LeadsIcon from '@/components/Icons/LeadsIcon.vue'
import ContactsIcon from '@/components/Icons/ContactsIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import Icon from '@/components/Icon.vue'
import { globalStore } from '@/stores/global'
import { usersStore } from '@/stores/users'
import { statusesStore } from '@/stores/statuses'
import { formatDate, timeAgo } from '@/utils'
import {
  Tabs,
  Tooltip,
  Badge,
  FeatherIcon,
  createResource,
  DateTimePicker,
  Toast,
  Dropdown,
  Button,
  Breadcrumbs,
  usePageMeta
} from 'frappe-ui'
import { h, computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const props = defineProps({
  campaignId: {
    type: String,
    required: true,
  },
})

const route = useRoute()
const router = useRouter()
const { $dialog } = globalStore()
const { getLeadStatus } = statusesStore()
const { getUser } = usersStore()
const campaignData = ref(null)
const error = ref(null)
const tabIndex = ref(0)
const isLoadingParticipants = ref(true)

// State for editing the scheduled time
const isEditingScheduledTime = ref(false)
const editedScheduledTime = ref(null)
const showSaveSuccess = ref(false)

// State for editing the status
const isEditingStatus = ref(false)
const editedStatus = ref(null)
const statusOptions = ref([])
const statusSelect = ref(null)

// Define the title computed property for document title
const title = computed(() => {
  return campaignData.value ? 
    (campaignData.value.campaign_name || campaignData.value.name || 'Unnamed Campaign') : 
    props.campaignId
})

const formattedStatusOptions = computed(() => {
  if (!statusOptions.value || !Array.isArray(statusOptions.value)) {
    return []
  }
  
  return statusOptions.value.map(option => {
    // If option is already an object with label and value
    if (option && typeof option === 'object' && option.label && option.value) {
      return option
    }
    
    // If option is a string, create an object
    if (typeof option === 'string') {
      return { label: option, value: option }
    }
    
    // Try to parse JSON if it's a string representation of an object
    if (typeof option === 'string' && option.includes('{')) {
      try {
        const parsed = JSON.parse(option)
        return parsed
      } catch (e) {
        // If parsing fails, use the string as is
        return { label: option, value: option }
      }
    }
    
    // Default fallback
    return { label: String(option), value: String(option) }
  })
})

// Use the page meta to set the document title
usePageMeta(() => {
  return {
    title: title.value,
    // Add favicon if needed
    // icon: brand.favicon,
  }
})

const breadcrumbs = computed(() => {
  return [
    { 
      label: __('Campaigns'), 
      route: { name: 'Campaigns' }
    },
    {
      label: title.value,
      route: { name: 'Campaign', params: { campaignId: props.campaignId } }
    }
  ]
})

// Get status color helper function
function getStatusColor(status) {
  const statusMap = {
    'Draft': 'text-gray-500',
    'Scheduled': 'text-blue-500',
    'In Progress': 'text-yellow-500',
    'Completed': 'text-green-500',
    'Cancelled': 'text-red-500'
  }
  
  return statusMap[status] || 'text-gray-500'
}

// Define tabs using the pattern from Organization.vue
const tabs = [
  {
    label: 'Leads',
    icon: h(LeadsIcon, { class: 'h-4 w-4' }),
    count: computed(() => leadParticipants.value?.length || 0),
  },
  {
    label: 'Contacts',
    icon: h(ContactsIcon, { class: 'h-4 w-4' }),
    count: computed(() => contactParticipants.value?.length || 0),
  },
]

onMounted(() => {
  loadCampaignData()
  fetchStatusOptions()
})

// Round date to nearest minute (remove seconds)
function roundToMinute(date) {
  if (!date) return null;
  const newDate = new Date(date);
  newDate.setSeconds(0);
  newDate.setMilliseconds(0);
  return newDate;
}

// Load campaign data
function loadCampaignData() {
  isLoadingParticipants.value = true
  
  const campaign = createResource({
    url: 'crm.fcrm.doctype.crm_campaign.crm_campaign.get_doc_view_campaign_data',
    params: { campaign_name: props.campaignId },
    onSuccess: (data) => {
      campaignData.value = data
      if (data.scheduled_send_time) {
        // Round to nearest minute when initializing
        editedScheduledTime.value = roundToMinute(new Date(data.scheduled_send_time))
      }
      if (data.status) {
        editedStatus.value = data.status
      }
      isLoadingParticipants.value = false
      console.log('Campaign data loaded:', data)
    },
    onError: (err) => {
      console.error('Failed to load campaign data:', err)
      error.value = err
      isLoadingParticipants.value = false
    }
  })

  campaign.fetch()
}

// Function to start editing the status
function startEditingStatus() {
  editedStatus.value = campaignData.value.status
  isEditingStatus.value = true
  
  // Focus the dropdown after it's rendered
  setTimeout(() => {
    if (isEditingStatus.value && statusSelect.value) {
      statusSelect.value.focus()
    }
  }, 10)
}

// Save updated status
// Save updated status
function saveStatus() {
  if (!editedStatus.value || editedStatus.value === campaignData.value.status) {
    isEditingStatus.value = false
    return
  }
  
  // Store the new status so we can update UI immediately
  const newStatus = editedStatus.value
  
  // Update UI immediately for a responsive feel
  const originalStatus = campaignData.value.status
  campaignData.value.status = newStatus
  
  const updateCampaign = createResource({
    url: 'crm.fcrm.doctype.crm_campaign.crm_campaign.update_campaign_status',
    params: {
      campaign_name: props.campaignId,
      status: newStatus
    },
    onSuccess: (data) => {
      // Show success message
      showSaveSuccess.value = true
      
      // Hide after 3 seconds
      setTimeout(() => {
        showSaveSuccess.value = false
      }, 3000)
      
      isEditingStatus.value = false
    },
    onError: (err) => {
      console.error('Failed to update status:', err)
      
      // Revert to original value if there was an error
      campaignData.value.status = originalStatus
      editedStatus.value = originalStatus
      
      isEditingStatus.value = false
      
      // Show error dialog
      $dialog({
        title: 'Error',
        message: 'Failed to update status. Please try again.',
      })
    }
  })
  
  // Close editing mode before submitting to avoid UI glitches
  isEditingStatus.value = false
  
  // Submit the update to the server
  updateCampaign.submit()
}

// Save updated scheduled time
function saveScheduledTime() {
  if (!editedScheduledTime.value) {
    isEditingScheduledTime.value = false
    return
  }

  const formattedDate = formatDateForFrappe(editedScheduledTime.value)

  const updateCampaign = createResource({
    url: 'crm.fcrm.doctype.crm_campaign.crm_campaign.update_campaign_scheduled_time',
    params: {
      campaign_name: props.campaignId,
      scheduled_send_time: formattedDate
    },
    onSuccess: (data) => {
      if (campaignData.value) {
        campaignData.value.scheduled_send_time = editedScheduledTime.value
      }
      showSaveSuccess.value = true
      setTimeout(() => {
        showSaveSuccess.value = false
      }, 3000)
      isEditingScheduledTime.value = false
    },
    onError: (err) => {
      console.error('Failed to update scheduled time:', err)
      if (campaignData.value) {
        editedScheduledTime.value = new Date(campaignData.value.scheduled_send_time)
      }
      isEditingScheduledTime.value = false
      $dialog({
        title: 'Error',
        message: 'Failed to update scheduled time. Please try again.',
      })
    }
  })

  updateCampaign.submit()
}

// Fetch status options from the doctype
function fetchStatusOptions() {
  const statusOptionsResource = createResource({
    url: 'crm.fcrm.doctype.crm_campaign.crm_campaign.get_crm_campaign_meta',
    params: {},
    onSuccess: (data) => {
      // Process the data if it's an array
      if (Array.isArray(data)) {
        statusOptions.value = data.map(item => {
          // Ensure we get clean objects with label and value
          if (typeof item === 'object' && item !== null) {
            return {
              label: item.label || item.value || String(item),
              value: item.value || item.label || String(item)
            }
          }
          return { label: String(item), value: String(item) }
        })
      } else {
        statusOptions.value = []
      }
    },
    onError: () => {
      statusOptions.value = []
    }
  })
  
  statusOptionsResource.fetch()
}

function onScheduledTimeChange(value) {
  if (!value) return

  // Ensure 'value' is a Date object
  const newDate = new Date(value)

  // Force seconds to 0
  newDate.setSeconds(0)
  newDate.setMilliseconds(0)

  // Update edited time
  editedScheduledTime.value = newDate

  // Now save
  saveScheduledTime()
}

function formatDateForFrappe(date) {
  const pad = (n) => (n < 10 ? '0' + n : n)
  return date.getFullYear() + '-' +
    pad(date.getMonth() + 1) + '-' +
    pad(date.getDate()) + ' ' +
    pad(date.getHours()) + ':' +
    pad(date.getMinutes()) + ':' +
    pad(date.getSeconds())
}

// Extract lead participants using a computed property
const leadParticipants = computed(() => {
  if (!campaignData.value || !campaignData.value.campaign_participants) {
    return []
  }
  
  // Find the CRM Lead array in campaign_participants
  for (const participantGroup of campaignData.value.campaign_participants) {
    if (participantGroup && participantGroup['CRM Lead']) {
      return participantGroup['CRM Lead']
    }
  }
  
  return []
})

// Extract contact participants using a computed property
const contactParticipants = computed(() => {
  if (!campaignData.value || !campaignData.value.campaign_participants) {
    return []
  }
  
  // Find the Contact array in campaign_participants
  for (const participantGroup of campaignData.value.campaign_participants) {
    if (participantGroup && participantGroup['Contact']) {
      return participantGroup['Contact']
    }
  }
  
  return []
})

// Map lead participants to the expected format for LeadsListView
const mappedLeadParticipants = computed(() => {
  if (!leadParticipants.value || !Array.isArray(leadParticipants.value)) {
    return []
  }
  
  return leadParticipants.value.map(lead => {
    return {
      name: lead.name || lead.reference_docname || '',
      full_name: {
        label: lead.full_name || lead.name || '',
        image_label: lead.full_name || lead.name || '',
        image: null,
      },
      organization: {
        label: lead.organization || '',
        logo: null,
      },
      email: lead.email || '',
      status: {
        label: lead.status || 'Open',
        color: getLeadStatus ? getLeadStatus(lead.status)?.color : 'text-green-500',
      },
      mobile_no: lead.mobile_no || '',
      participant_source: lead.participant_source || 'CRM Lead',
      reference_docname: lead.reference_docname || '',
      modified: lead.modified ? {
        label: formatDate(lead.modified),
        timeAgo: timeAgo(lead.modified),
      } : null,
    }
  })
})

// Map contact participants to the expected format for ContactsListView
const mappedContactParticipants = computed(() => {
  if (!contactParticipants.value || !Array.isArray(contactParticipants.value)) {
    return []
  }
  
  return contactParticipants.value.map(contact => {
    return {
      name: contact.name || contact.reference_docname || '',
      full_name: {
        label: contact.full_name || contact.name || '',
        image_label: contact.full_name || contact.name || '',
        image: null,
      },
      organization: {
        label: contact.organization || contact.company_name || '',
        logo: null,
      },
      email: contact.email || contact.email_id || '',
      mobile_no: contact.mobile_no || '',
      participant_source: contact.participant_source || 'Contact',
      reference_docname: contact.reference_docname || '',
      modified: contact.modified ? {
        label: formatDate(contact.modified),
        timeAgo: timeAgo(contact.modified),
      } : null,
    }
  })
})

// Column definitions for leads
const leadColumns = [
  {
    label: __('Name'),
    key: 'full_name',
    width: '11rem',
  },
  {
    label: __('Organization'),
    key: 'organization',
    width: '9rem',
  },
  {
    label: __('Email'),
    key: 'email',
    width: '10rem',
  },
  {
    label: __('Mobile'),
    key: 'mobile_no',
    width: '8rem',
  },
  {
    label: __('Status'),
    key: 'status',
    width: '8rem',
  },
  {
    label: __('Source'),
    key: 'participant_source',
    width: '12rem',
  },
  {
    label: __('Reference Document'),
    key: 'reference_docname',
    width: '11rem',
  }
]

// Column definitions for contacts
const contactColumns = [
  {
    label: __('Name'),
    key: 'full_name',
    width: '11rem',
  },
  {
    label: __('Organization'),
    key: 'organization',
    width: '9rem',
  },
  {
    label: __('Email'),
    key: 'email',
    width: '10rem',
  },
  {
    label: __('Mobile'),
    key: 'mobile_no',
    width: '8rem',
  },
  {
    label: __('Source'),
    key: 'participant_source',
    width: '12rem',
  },
  {
    label: __('Reference Document'),
    key: 'reference_docname',
    width: '11rem',
  }
]
</script>