<template>
  <div v-if="campaignData" class="flex flex-1 flex-col overflow-hidden">
    <!-- Header section with campaign details -->
    <div class="flex items-start justify-start gap-6 p-5 sm:items-center">
      <div class="flex flex-col justify-center gap-2 sm:gap-0.5">
        <div class="text-3xl font-semibold text-gray-900">
          {{ campaignData.campaign_name }}
        </div>
        <div class="flex flex-col flex-wrap gap-3 text-base text-gray-700 sm:flex-row sm:items-center sm:gap-2">
          <!-- Campaign Type -->
          <div class="flex items-center gap-1.5">
            <FeatherIcon name="tag" class="h-4 w-4" />
            <span>{{ campaignData.campaign_type }}</span>
          </div>

          <!-- Separator -->
          <span class="hidden text-3xl leading-[0] text-gray-600 sm:flex">
            &middot;
          </span>
          
          <!-- Status -->
          <div class="flex items-center gap-1.5">
            <FeatherIcon name="bookmark" class="h-4 w-4" />
            <span>{{ campaignData.status }}</span>
          </div>

          <!-- Scheduled Time -->
          <span v-if="campaignData.scheduled_send_time" class="hidden text-3xl leading-[0] text-gray-600 sm:flex">
            &middot;
          </span>
          <div v-if="campaignData.scheduled_send_time" class="flex items-center gap-1.5">
            <FeatherIcon name="calendar" class="h-4 w-4" />
            <span>{{ formatDate(campaignData.scheduled_send_time, 'MMM D, YYYY h:mm A') }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Debug -->
    <div class="p-4 border rounded bg-gray-50 mb-4 mx-4">
      <h3 class="font-medium text-gray-900 mb-2">Raw Leads:</h3>
      <pre class="text-xs overflow-auto max-h-40 mb-2">{{ JSON.stringify(leadParticipants, null, 2) }}</pre>
    </div>

    <!-- Simple tabs -->
    <div class="border-b border-gray-200">
      <nav class="flex -mb-px">
        <button 
          @click="activeTab = 'leads'"
          class="py-4 px-6 font-medium text-sm border-b-2 transition-colors"
          :class="activeTab === 'leads' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
        >
          Leads ({{ leadParticipants.length }})
        </button>
        <button 
          @click="activeTab = 'contacts'"
          class="py-4 px-6 font-medium text-sm border-b-2 transition-colors"
          :class="activeTab === 'contacts' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
        >
          Contacts ({{ contactParticipants.length }})
        </button>
      </nav>
    </div>

    <!-- Tab content -->
    <div class="p-4">
      <!-- Leads tab -->
      <div v-if="activeTab === 'leads'" class="space-y-4">
        <h2 class="text-lg font-medium">Campaign Leads</h2>
        
        <div v-if="leadParticipants.length === 0" class="text-center py-8 text-gray-500">
          No leads found for this campaign
        </div>
        
        <table v-else class="min-w-full divide-y divide-gray-200 border">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Organization</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reference</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="lead in leadParticipants" :key="lead.reference_docname">
              <td class="px-4 py-3 whitespace-nowrap text-sm">{{ lead.full_name }}</td>
              <td class="px-4 py-3 whitespace-nowrap text-sm">{{ lead.organization }}</td>
              <td class="px-4 py-3 whitespace-nowrap text-sm">{{ lead.email }}</td>
              <td class="px-4 py-3 whitespace-nowrap text-sm">{{ lead.reference_docname }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Contacts tab -->
      <div v-if="activeTab === 'contacts'" class="space-y-4">
        <h2 class="text-lg font-medium">Campaign Contacts</h2>
        
        <div v-if="contactParticipants.length === 0" class="text-center py-8 text-gray-500">
          No contacts found for this campaign
        </div>
        
        <table v-else class="min-w-full divide-y divide-gray-200 border">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Organization</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reference</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="contact in contactParticipants" :key="contact.reference_docname">
              <td class="px-4 py-3 whitespace-nowrap text-sm">{{ contact.full_name }}</td>
              <td class="px-4 py-3 whitespace-nowrap text-sm">{{ contact.organization || contact.company_name }}</td>
              <td class="px-4 py-3 whitespace-nowrap text-sm">{{ contact.email || contact.email_id }}</td>
              <td class="px-4 py-3 whitespace-nowrap text-sm">{{ contact.reference_docname }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
  
  <!-- Loading State -->
  <div v-else class="flex-1 grid place-items-center">
    <div class="flex flex-col items-center justify-center space-y-3">
      <FeatherIcon name="loader" class="h-10 w-10 animate-spin" />
      <div class="text-lg text-gray-600">Loading Campaign...</div>
    </div>
  </div>
</template>

<script setup>
import { formatDate } from '@/utils'
import { FeatherIcon, createResource } from 'frappe-ui'
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  campaignId: {
    type: String,
    required: true,
  },
})

const campaignData = ref(null)
const activeTab = ref('leads')
const isLoading = ref(true)

onMounted(() => {
  console.log('Campaign view mounted, loading campaign:', props.campaignId)
  loadCampaignData()
})

// Load campaign data
function loadCampaignData() {
  isLoading.value = true
  
  const campaign = createResource({
    url: 'crm.fcrm.doctype.crm_campaign.crm_campaign.get_doc_view_campaign_data',
    params: { campaign_name: props.campaignId },
    onSuccess: (data) => {
      console.log('Campaign data loaded:', data)
      campaignData.value = data
      isLoading.value = false
    },
    onError: (err) => {
      console.error('Failed to load campaign data:', err)
      isLoading.value = false
    }
  })

  campaign.fetch()
}

// Extract lead participants directly using a computed property
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
</script>