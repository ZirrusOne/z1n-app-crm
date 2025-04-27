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

    <!-- Tabs section using the same pattern as Organization.vue -->
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
  Tabs,
  Tooltip,
  Badge,
  FeatherIcon,
  createResource,
} from 'frappe-ui'
import { h, computed, ref, onMounted } from 'vue'
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