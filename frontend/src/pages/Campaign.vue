<template>
  <div v-if="campaignData" class="flex flex-1 flex-col overflow-hidden">
    <!-- Header section with campaign details -->
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

          <!-- Separator -->
          <span v-if="campaignData.campaign_type && campaignData.status" 
                class="hidden text-3xl leading-[0] text-gray-600 sm:flex">
            &middot;
          </span>
          
          <!-- Status -->
          <Tooltip text="Status" v-if="campaignData.status">
            <div class="flex items-center gap-1.5">
              <FeatherIcon name="bookmark" class="h-4 w-4" />
              <span class="">{{ campaignData.status }}</span>
            </div>
          </Tooltip>

          <!-- Scheduled Time -->
          <span v-if="campaignData.scheduled_send_time" class="hidden text-3xl leading-[0] text-gray-600 sm:flex">
            &middot;
          </span>
          <Tooltip text="Scheduled Time" v-if="campaignData.scheduled_send_time">
            <div class="flex items-center gap-1.5">
              <FeatherIcon name="calendar" class="h-4 w-4" />
              <span class="">{{ formatDate(campaignData.scheduled_send_time, 'MMM D, YYYY h:mm A') }}</span>
            </div>
          </Tooltip>
        </div>
      </div>
    </div>

    <!-- Using simple div-based tabs as a workaround -->
    <div class="flex border-b px-5">
      <div 
        class="flex items-center gap-2 px-4 py-2.5 cursor-pointer"
        :class="tabIndex === 0 ? 'border-b-2 border-blue-500 text-gray-900 font-medium' : 'text-gray-600'"
        @click="tabIndex = 0"
      >
        <LeadsIcon class="h-4 w-4" />
        <span>{{ __('Leads') }}</span>
        <span class="ml-1 text-sm text-gray-500">({{ leadParticipants.length || 0 }})</span>
      </div>
      <div 
        class="flex items-center gap-2 px-4 py-2.5 cursor-pointer"
        :class="tabIndex === 1 ? 'border-b-2 border-blue-500 text-gray-900 font-medium' : 'text-gray-600'"
        @click="tabIndex = 1"
      >
        <ContactsIcon class="h-4 w-4" />
        <span>{{ __('Contacts') }}</span>
        <span class="ml-1 text-sm text-gray-500">({{ contactParticipants.length || 0 }})</span>
      </div>
    </div>

    <!-- Tab content -->
    <div class="p-5">
      <!-- Loading State -->
      <div v-if="isLoadingParticipants" class="flex justify-center py-8">
        <div>{{ __('Loading data...') }}</div>
      </div>
      
      <!-- Leads Tab Content -->
      <div v-else-if="tabIndex === 0">
        <div v-if="mappedLeadParticipants.length">
          <LeadsListView
            :rows="mappedLeadParticipants"
            :columns="leadColumns"
            :options="{ selectable: false, showTooltip: true }"
          />
        </div>
        <div v-else class="grid flex-1 place-items-center text-xl font-medium text-gray-500 p-10">
          <div class="flex flex-col items-center justify-center space-y-3">
            <LeadsIcon class="h-10 w-10" />
            <div>{{ __('No Leads Found') }}</div>
          </div>
        </div>
      </div>
      
      <!-- Contacts Tab Content -->
      <div v-else-if="tabIndex === 1">
        <div v-if="mappedContactParticipants.length">
          <ContactsListView
            :rows="mappedContactParticipants"
            :columns="contactColumns"
            :options="{ selectable: false, showTooltip: true }"
          />
        </div>
        <div v-else class="grid flex-1 place-items-center text-xl font-medium text-gray-500 p-10">
          <div class="flex flex-col items-center justify-center space-y-3">
            <ContactsIcon class="h-10 w-10" />
            <div>{{ __('No Contacts Found') }}</div>
          </div>
        </div>
      </div>
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
import { globalStore } from '@/stores/global'
import { usersStore } from '@/stores/users'
import { statusesStore } from '@/stores/statuses'
import { formatDate, timeAgo } from '@/utils'
import {
  Tooltip,
  FeatherIcon,
  createResource,
} from 'frappe-ui'
import { computed, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  campaignId: {
    type: String,
    required: true,
  },
})

const { $dialog } = globalStore()
const { getLeadStatus } = statusesStore()
const { getUser } = usersStore()
const campaignData = ref(null)
const error = ref(null)
const tabIndex = ref(0)
const isLoadingParticipants = ref(true)

onMounted(() => {
  loadCampaignData()
})

// Load campaign data
function loadCampaignData() {
  isLoadingParticipants.value = true
  
  const campaign = createResource({
    url: 'crm.fcrm.doctype.crm_campaign.crm_campaign.get_doc_view_campaign_data',
    params: { campaign_name: props.campaignId },
    onSuccess: (data) => {
      campaignData.value = data
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