<template>
  <LayoutHeader v-if="deal.data">
    <template #left-header>
      <Breadcrumbs :items="breadcrumbs">
        <template #prefix="{ item }">
          <Icon v-if="item.icon" :icon="item.icon" class="mr-2 h-4" />
        </template>
      </Breadcrumbs>
    </template>
    <template #right-header>
<<<<<<< HEAD
      <CustomActions
        v-if="deal.data._customActions?.length"
        :actions="deal.data._customActions"
      />
      <AssignTo
        v-model="deal.data._assignedTo"
        :data="deal.data"
        doctype="CRM Deal"
      />
      <Dropdown
        :options="statusOptions('deal', updateField, deal.data._customStatuses)"
      >
=======
      <CustomActions v-if="customActions" :actions="customActions" />
      <component :is="deal.data._assignedTo?.length == 1 ? 'Button' : 'div'">
        <MultipleAvatar
          :avatars="deal.data._assignedTo"
          @click="showAssignmentModal = true"
        />
      </component>
      <Dropdown :options="statusOptions('deal', updateField, customStatuses)" class="status-option">
>>>>>>> origin/Scrum-9-z1
        <template #default="{ open }">
          <Button :label="deal.data.status">
            <template #prefix>
              <IndicatorIcon :class="getDealStatus(deal.data.status).color" />
            </template>
            <template #suffix>
              <FeatherIcon
                :name="open ? 'chevron-up' : 'chevron-down'"
                class="h-4"
              />
            </template>
          </Button>
        </template>
      </Dropdown>
      <select v-model="deal.data.status_detail" class="rounded h-7 text-base px-2 border border-gray-100 bg-gray-100 hover:border-gray-200 hover:bg-gray-200 focus:border-gray-500 focus:ring-0 focus-visible:ring-2 focus-visible:ring-gray-400 text-gray-800 transition-colors w-full py-0 status-option-detail" 
      @change.stop="updateStatusDetail($event.target.value)"
      >
          <option 
          v-for="(option, index) in staus_detail_option" 
          :key="index" 
          :title="option.dec" 
          :value="option.name"
          >
          {{ option.name }}
          </option>
      </select>
    </template>

  </LayoutHeader>
  <div v-if="deal.data" class="flex h-full overflow-hidden">
    <Tabs as="div" v-model="tabIndex" :tabs="tabs">
      <template #tab-panel>
        <Activities
          ref="activities"
          doctype="CRM Deal"
          :tabs="tabs"
          v-model:reload="reload"
          v-model:tabIndex="tabIndex"
          v-model="deal"
        />
      </template>
    </Tabs>
    <Resizer side="right" class="flex flex-col justify-between border-l">
      <div
        class="flex h-10.5 cursor-copy items-center border-b px-5 py-2.5 text-lg font-medium text-ink-gray-9"
        @click="copyToClipboard(deal.data.name)"
      >
        {{ __(deal.data.name) }}
      </div>
      <div class="flex items-center justify-start gap-5 border-b p-5">
        <Tooltip :text="__('Organization logo')">
          <div class="group relative size-12">
            <Avatar
              size="3xl"
              class="size-12"
              :label="organization.data?.name || __('Untitled')"
              :image="organization.data?.organization_logo"
            />
          </div>
        </Tooltip>
        <div class="flex flex-col gap-2.5 truncate text-ink-gray-9">
          <Tooltip :text="organization.data?.name || __('Set an organization')">
            <div class="truncate text-2xl font-medium">
              {{ organization.data?.name || __('Untitled') }}
            </div>
          </Tooltip>
          <div class="flex gap-1.5">
            <Tooltip v-if="callEnabled" :text="__('Make a call')">
              <Button class="h-7 w-7" @click="triggerCall">
                <PhoneIcon class="h-4 w-4" />
              </Button>
            </Tooltip>
            <Tooltip :text="__('Send an email')">
              <Button class="h-7 w-7">
                <Email2Icon
                  class="h-4 w-4"
                  @click="
                    deal.data.email
                      ? openEmailBox()
                      : errorMessage(__('No email set'))
                  "
                />
              </Button>
            </Tooltip>
            <Tooltip :text="__('Go to website')">
              <Button class="h-7 w-7">
                <LinkIcon
                  class="h-4 w-4"
                  @click="
                    deal.data.website
                      ? openWebsite(deal.data.website)
                      : errorMessage(__('No website set'))
                  "
                />
              </Button>
            </Tooltip>
            <Tooltip :text="__('Attach a file')">
              <Button class="size-7" @click="showFilesUploader = true">
                <AttachmentIcon class="size-4" />
              </Button>
            </Tooltip>
          </div>
        </div>
      </div>
      <SLASection
        v-if="deal.data.sla_status"
        v-model="deal.data"
        @updateField="updateField"
      />

      <div
        v-if="sections.data"
        class="flex flex-1 flex-col justify-between overflow-hidden"
      >
<<<<<<< HEAD
        <SidePanelLayout
          v-model="deal.data"
          :sections="sections.data"
          :addContact="addContact"
          doctype="CRM Deal"
          v-slot="{ section }"
          @update="updateField"
          @reload="sections.reload"
        >
          <div v-if="section.name == 'contacts_section'" class="contacts-area">
            <div
              v-if="dealContacts?.loading && dealContacts?.data?.length == 0"
              class="flex min-h-20 flex-1 items-center justify-center gap-3 text-base text-ink-gray-4"
            >
              <LoadingIndicator class="h-4 w-4" />
              <span>{{ __('Loading...') }}</span>
            </div>
            <div
              v-else-if="dealContacts?.data?.length"
              v-for="(contact, i) in dealContacts.data"
              :key="contact.name"
            >
              <div class="px-2 pb-2.5" :class="[i == 0 ? 'pt-5' : 'pt-2.5']">
                <Section :opened="contact.opened">
                  <template #header="{ opened, toggle }">
                    <div
                      class="flex cursor-pointer items-center justify-between gap-2 pr-1 text-base leading-5 text-ink-gray-7"
                    >
=======
        <div class="flex flex-col overflow-y-auto">
          <div  class="section flex flex-col p-3">

            <!-- Manage custom deal elements-->
            <Section :label="'Deal Details'">
              <div class="px-8 pb-3 flex flex-wrap items-start text-sm text-gray-600">Deal element : </div>
              <div class="px-8 flex flex-wrap items-start gap-3 text-sm text-gray-600">
                <MultiSelectDealElement
                class="flex-1"
                v-model="dealElementNames"
                :deal-name="deal.data.name"
                />
              </div>
            </Section>
           <div
            v-for="(section, i) in fieldsLayout.data"
            :key="section.label"
            class="section flex flex-col p-3"
            :class="{ '': i !== fieldsLayout.data.length - 1 }"
          >
            <SectionDeal :is-opened="section.opened" :label="section.label" v-if=" section.label  == 'Organization Details'">
              <template #actions>
                <div v-if="section.organization" class="pr-2">
                 
                </div>
              
              </template>
              <SectionFieldsDetails
                v-if="section.fields"
                :fields="section.fields"
                :crm_deal_probability="crm_deal_probability"
                :crm_deal_annual_revenue="crm_deal_annual_revenue"
                :crm_deal_weighted_amount="crm_deal_weighted_amount"
                :isLastSection="i == fieldsLayout.data.length - 1"
                v-model="deal.data"
                @update="updateField"
              />
            </SectionDeal>
          </div>
          </div>
          <div
            v-for="(section, i) in fieldsLayout.data"
            :key="section.label"
            class="section flex flex-col p-3"
            :class="{ 'border-b': i !== fieldsLayout.data.length - 1 }"
          >
            <Section :is-opened="section.opened" :label="section.label">
              <template #actions>
                <div v-if="section.contacts" class="pr-2">
                  <Link
                    value=""
                    doctype="Contact"
                    @change="(e) => addContact(e)"
                    :onCreate="
                      (value, close) => {
                        _contact = {
                          first_name: value,
                          company_name: deal.data.organization,
                        }
                        showContactModal = true
                        close()
                      }
                    "
                  >
                    <template #target="{ togglePopover }">
                      <Button
                        class="h-7 px-3"
                        variant="ghost"
                        icon="plus"
                        @click="togglePopover()"
                      />
                    </template>
                  </Link>
                </div>
                <Button
                  v-else-if="
                    ((!section.contacts && i == 1) || i == 0) && isManager()
                  "
                  variant="ghost"
                  class="w-7 mr-2"
                  @click="showSidePanelModal = true"
                >
                  <EditIcon class="h-4 w-4" />
                </Button>
              </template>
              <SectionFieldsDeal
                v-if="section.fields"
                :fields="section.fields"
                :isLastSection="i == fieldsLayout.data.length - 1"
                v-model="deal.data"
                @update="updateField"
              />
              <div v-else>
                <div
                  v-if="
                    dealContacts?.loading && dealContacts?.data?.length == 0
                  "
                  class="flex min-h-20 flex-1 items-center justify-center gap-3 text-base text-gray-500"
                >
                  <LoadingIndicator class="h-4 w-4" />
                  <span>{{ __('Loading...') }}</span>
                </div>
                <div
                  v-else-if="dealContacts?.data?.length"
                  v-for="(contact, i) in dealContacts.data"
                  :key="contact.name"
                >
                  <div
                    class="px-2 pb-2.5"
                    :class="[i == 0 ? 'pt-5' : 'pt-2.5']"
                  >
                    <Section :is-opened="contact.opened">
                      <template #header="{ opened, toggle }">
                        <div
                          class="flex cursor-pointer items-center justify-between gap-2 pr-1 text-base leading-5 text-gray-700"
                        >
                          <div
                            class="flex h-7 items-center gap-2 truncate"
                            @click="toggle()"
                          >
                            <Avatar
                              :label="contact.full_name"
                              :image="contact.image"
                              size="md"
                            />
                            <div class="truncate">
                              {{ contact.full_name }}
                            </div>
                            <Badge
                              v-if="contact.is_primary"
                              class="ml-2"
                              variant="outline"
                              :label="__('Primary')"
                              theme="green"
                            />
                          </div>
                          <div class="flex items-center">
                            <Dropdown :options="contactOptions(contact)">
                              <Button
                                icon="more-horizontal"
                                class="text-gray-600"
                                variant="ghost"
                              />
                            </Dropdown>
                            <Button
                              variant="ghost"
                              @click="
                                router.push({
                                  name: 'Contact',
                                  params: { contactId: contact.name },
                                })
                              "
                            >
                              <ArrowUpRightIcon class="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" @click="toggle()">
                              <FeatherIcon
                                name="chevron-right"
                                class="h-4 w-4 text-gray-900 transition-all duration-300 ease-in-out"
                                :class="{ 'rotate-90': opened }"
                              />
                            </Button>
                          </div>
                        </div>
                      </template>
>>>>>>> origin/Scrum-9-z1
                      <div
                        class="flex h-7 items-center gap-2 truncate"
                        @click="toggle()"
                      >
                        <Avatar
                          :label="contact.full_name"
                          :image="contact.image"
                          size="md"
                        />
                        <div class="truncate">
                          {{ contact.full_name }}
                        </div>
<<<<<<< HEAD
                        <Badge
                          v-if="contact.is_primary"
                          class="ml-2"
                          variant="outline"
                          :label="__('Primary')"
                          theme="green"
                        />
=======
                        <div  class="flex items-center gap-3 p-1 py-1.5">
                          <PriceTagIcon class="h-4 w-4 pricetag" />
                          {{ contact.custom_buying_role }}
                        </div>
>>>>>>> origin/Scrum-9-z1
                      </div>
                      <div class="flex items-center">
                        <Dropdown :options="contactOptions(contact)">
                          <Button
                            icon="more-horizontal"
                            class="text-ink-gray-5"
                            variant="ghost"
                          />
                        </Dropdown>
                        <Button
                          variant="ghost"
                          @click="
                            router.push({
                              name: 'Contact',
                              params: { contactId: contact.name },
                            })
                          "
                        >
                          <ArrowUpRightIcon class="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" @click="toggle()">
                          <FeatherIcon
                            name="chevron-right"
                            class="h-4 w-4 text-ink-gray-9 transition-all duration-300 ease-in-out"
                            :class="{ 'rotate-90': opened }"
                          />
                        </Button>
                      </div>
                    </div>
                  </template>
                  <div class="flex flex-col gap-1.5 text-base text-ink-gray-8">
                    <div class="flex items-center gap-3 pb-1.5 pl-1 pt-4">
                      <Email2Icon class="h-4 w-4" />
                      {{ contact.email }}
                    </div>
                    <div class="flex items-center gap-3 p-1 py-1.5">
                      <PhoneIcon class="h-4 w-4" />
                      {{ contact.mobile_no }}
                    </div>
                  </div>
                </Section>
              </div>
              <div
                v-if="i != dealContacts.data.length - 1"
                class="mx-2 h-px border-t border-outline-gray-modals"
              />
            </div>
            <div
              v-else
              class="flex h-20 items-center justify-center text-base text-ink-gray-5"
            >
              {{ __('No contacts added') }}
            </div>
          </div>
        </SidePanelLayout>
      </div>
    </Resizer>
  </div>
  <OrganizationModal
    v-model="showOrganizationModal"
    v-model:organization="_organization"
    :options="{
      redirect: false,
      afterInsert: (doc) => updateField('organization', doc.name),
    }"
  />
  <ContactModal
    v-model="showContactModal"
    :contact="_contact"
    :options="{
      redirect: false,
      afterInsert: (doc) => addContact(doc.name),
    }"
  />
  <FilesUploader
    v-if="deal.data?.name"
    v-model="showFilesUploader"
    doctype="CRM Deal"
    :docname="deal.data.name"
    @after="
      () => {
        activities?.all_activities?.reload()
        changeTabTo('attachments')
      }
    "
  />
</template>
<script setup>
import Icon from '@/components/Icon.vue'
import Resizer from '@/components/Resizer.vue'
import LoadingIndicator from '@/components/Icons/LoadingIndicator.vue'
import ActivityIcon from '@/components/Icons/ActivityIcon.vue'
import EmailIcon from '@/components/Icons/EmailIcon.vue'
import Email2Icon from '@/components/Icons/Email2Icon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import DetailsIcon from '@/components/Icons/DetailsIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import WhatsAppIcon from '@/components/Icons/WhatsAppIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import LinkIcon from '@/components/Icons/LinkIcon.vue'
import ArrowUpRightIcon from '@/components/Icons/ArrowUpRightIcon.vue'
import SuccessIcon from '@/components/Icons/SuccessIcon.vue'
import AttachmentIcon from '@/components/Icons/AttachmentIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import Activities from '@/components/Activities/Activities.vue'
import OrganizationModal from '@/components/Modals/OrganizationModal.vue'
import AssignTo from '@/components/AssignTo.vue'
import FilesUploader from '@/components/FilesUploader/FilesUploader.vue'
import ContactModal from '@/components/Modals/ContactModal.vue'
import Section from '@/components/Section.vue'
<<<<<<< HEAD
import SidePanelLayout from '@/components/SidePanelLayout.vue'
=======
import SectionDeal from '@/components/SectionDeal.vue'
import SectionFieldsDeal from '@/components/SectionFieldsDeal.vue'
import SectionFieldsDetails from '@/components/SectionFieldsDetail.vue'

>>>>>>> origin/Scrum-9-z1
import SLASection from '@/components/SLASection.vue'
import CustomActions from '@/components/CustomActions.vue'
import {
  openWebsite,
  createToast,
  setupAssignees,
  setupCustomizations,
  errorMessage,
  copyToClipboard,
  customFormatNumberIntoCurrency
} from '@/utils'
import { getView } from '@/utils/view'
import { getSettings } from '@/stores/settings'
import { globalStore } from '@/stores/global'
import { statusesStore } from '@/stores/statuses'
import { whatsappEnabled, callEnabled } from '@/composables/settings'
import {
  createResource,
  Dropdown,
  Tooltip,
  Avatar,
  Tabs,
  Breadcrumbs,
  call,
  usePageMeta,
  FormControl
} from 'frappe-ui'
import { ref, computed, h, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useActiveTabManager } from '@/composables/useActiveTabManager'
import PriceTagIcon from '@/components/Icons/PriceTagIcon.vue'
import MultiSelectDealElement from '../components/Controls/MultiSelectDealElement.vue'  
 

const { brand } = getSettings()
const { $dialog, $socket, makeCall } = globalStore()
const { statusOptions, getDealStatus } = statusesStore()
const route = useRoute()
const router = useRouter()
const dealElements = ref([]); // Array to store deal elements
const dealElementNames = ref([]); // Array to store only names of deal elements

const props = defineProps({
  dealId: {
    type: String,
    required: true,
  },
})

<<<<<<< HEAD
const deal = createResource({
  url: 'crm.fcrm.doctype.crm_deal.api.get_deal',
  params: { name: props.dealId },
  cache: ['deal', props.dealId],
  onSuccess: (data) => {
=======
const customActions = ref([])
const customStatuses = ref([])
const staus_detail_option = ref([]);
const crm_deal_annual_revenue = ref();
const crm_deal_probability = ref();
const crm_deal_weighted_amount = ref();



const deal = createResource({
  url: 'crm.fcrm.doctype.crm_deal.api.get_deal',
  params: { name: props.dealId },
  onSuccess: async (data) => {
    crm_deal_probability.value = data.probability
    crm_deal_annual_revenue.value = data.annual_revenue;
    crm_deal_weighted_amount.value = data.weighted_amount;


    if (data.probability || data.probability === 0) {
      data.probability = data.probability + '%'; 
    }
   if (data.annual_revenue ) {
      data.annual_revenue = customFormatNumberIntoCurrency(data.annual_revenue, data.currency); 
    }
    if (data.weighted_amount ) {
      data.weighted_amount = customFormatNumberIntoCurrency(data.weighted_amount, data.currency); 
    }
>>>>>>> origin/Scrum-9-z1
    if (data.organization) {
      organization.update({
        params: { doctype: 'CRM Organization', name: data.organization },
      })
      organization.fetch()
    }

    setupAssignees(deal)
    setupCustomizations(deal, {
      doc: data,
      $dialog,
      $socket,
      router,
      updateField,
      createToast,
      deleteDoc: deleteDeal,
      resource: {
        deal,
        dealContacts,
        sections,
      },
      call,
<<<<<<< HEAD
    })
=======
    }
    setupAssignees(data)
    let customization = await setupCustomizations(data, obj)
    dealElements.value = data.child_tables.deal_elements || [];
    dealElementNames.value = dealElements.value.map(element => element.deal_elements);

    customActions.value = customization.actions || []
    customStatuses.value = customization.statuses || []
>>>>>>> origin/Scrum-9-z1
  },
})

const organization = createResource({
  url: 'frappe.client.get',
  onSuccess: (data) => (deal.data._organizationObj = data),
})

onMounted(() => {
  $socket.on('crm_customer_created', () => {
    createToast({
      title: __('Customer created successfully'),
      icon: 'check',
      iconClasses: 'text-ink-green-3',
    })
  })

  if (deal.data) {
    organization.data = deal.data._organizationObj
    return
  }
  deal.fetch().then(() => {
      getStatusDetail(deal.data.status)
    })

})

onBeforeUnmount(() => {
  $socket.off('crm_customer_created')
})

function getStatusDetail(status) {
  createResource({
  auto: true,
  params: {
      status: status,
    },
  url: 'crm.api.doc.get_crm_deal_status_for_status',
  transform: (data) => {
    const actualData = unwrapProxy(data);

    if (!actualData || !Array.isArray(actualData)) {
    staus_detail_option.value = [];
    }
    // const status_array = actualData.map((item) => item.detail_name);
    // staus_detail_option.value = status_array;
    const status_array = actualData.map((item) => ({
        name: item.detail_name, // Adjust if `detail_name` is not the correct key
        dec: item.description || '' // Adjust if `detail_description` is not the correct key or needs a default
      }));

      staus_detail_option.value = status_array;
  },

});
}
function updateStatusDetail(value){
updateDeal('status_detail', value, () => {
    deal.data['status_detail'] = value
  })
}

/**
 *  Convert proxy object into array
 * @param proxyData 
 */
 function unwrapProxy(proxyData) {
  if (Array.isArray(proxyData)) {
    return proxyData.map((item) => unwrapProxy(item));
  } 
  else if (proxyData !== null && typeof proxyData === 'object') {
    return Object.keys(proxyData).reduce((acc, key) => {
      acc[key] = unwrapProxy(proxyData[key]);
      return acc;
    }, {});
  }
  return proxyData;
}

const reload = ref(false)
const showOrganizationModal = ref(false)
const showFilesUploader = ref(false)
const _organization = ref({})

function updateDeal(fieldname, value, callback) {
  value = Array.isArray(fieldname) ? '' : value

  if (validateRequired(fieldname, value)) return

  createResource({
    url: 'frappe.client.set_value',
    params: {
      doctype: 'CRM Deal',
      name: props.dealId,
      fieldname,
      value,
    },
    auto: true,
    onSuccess: () => {
      deal.reload()
      reload.value = true
      createToast({
        title: __('Deal updated'),
        icon: 'check',
        iconClasses: 'text-ink-green-3',
      })
      callback?.()
    },
    onError: (err) => {
      createToast({
        title: __('Error updating deal'),
        text: __(err.messages?.[0]),
        icon: 'x',
        iconClasses: 'text-ink-red-4',
      })
    },
  })
}

function validateRequired(fieldname, value) {
  let meta = deal.data.fields_meta || {}
  if (meta[fieldname]?.reqd && !value) {
    createToast({
      title: __('Error Updating Deal'),
      text: __('{0} is a required field', [meta[fieldname].label]),
      icon: 'x',
      iconClasses: 'text-ink-red-4',
    })
    return true
  }
  return false
}

const breadcrumbs = computed(() => {
  let items = [{ label: __('Deals'), route: { name: 'Deals' } }]

  if (route.query.view || route.query.viewType) {
    let view = getView(route.query.view, route.query.viewType, 'CRM Deal')
    if (view) {
      items.push({
        label: __(view.label),
        icon: view.icon,
        route: {
          name: 'Deals',
          params: { viewType: route.query.viewType },
          query: { view: route.query.view },
        },
      })
    }
  }

  items.push({
    label: organization.data?.name || __('Untitled'),
    route: { name: 'Deal', params: { dealId: deal.data.name } },
  })
  return items
})

usePageMeta(() => {
  return {
    title: organization.data?.name || deal.data?.name,
    icon: brand.favicon,
  }
})

const tabs = computed(() => {
  let tabOptions = [
    {
      name: 'Activity',
      label: __('Activity'),
      icon: ActivityIcon,
    },
    {
      name: 'Emails',
      label: __('Emails'),
      icon: EmailIcon,
    },
    {
      name: 'Comments',
      label: __('Comments'),
      icon: CommentIcon,
    },
    {
      name: 'Data',
      label: __('Data'),
      icon: DetailsIcon,
    },
    {
      name: 'Calls',
      label: __('Calls'),
      icon: PhoneIcon,
      condition: () => callEnabled.value,
    },
    {
      name: 'Tasks',
      label: __('Tasks'),
      icon: TaskIcon,
    },
    {
      name: 'Notes',
      label: __('Notes'),
      icon: NoteIcon,
    },
    {
      name: 'Attachments',
      label: __('Attachments'),
      icon: AttachmentIcon,
    },
    {
      name: 'WhatsApp',
      label: __('WhatsApp'),
      icon: WhatsAppIcon,
      condition: () => whatsappEnabled.value,
    },
  ]
  return tabOptions.filter((tab) => (tab.condition ? tab.condition() : true))
})
const { tabIndex } = useActiveTabManager(tabs, 'lastDealTab')

const sections = createResource({
  url: 'crm.fcrm.doctype.crm_fields_layout.crm_fields_layout.get_sidepanel_sections',
  cache: ['sidePanelSections', 'CRM Deal'],
  params: { doctype: 'CRM Deal' },
  auto: true,
  transform: (data) => getParsedSections(data),
})

function getParsedSections(_sections) {
  _sections.forEach((section) => {
    if (section.name == 'contacts_section') return
    section.columns[0].fields.forEach((field) => {
      if (field.fieldname == 'organization') {
        field.create = (value, close) => {
          _organization.value.organization_name = value
          showOrganizationModal.value = true
          close()
        }
        field.link = (org) =>
          router.push({
            name: 'Organization',
            params: { organizationId: org },
          })
      }
    })
  })
  return _sections
}

const showContactModal = ref(false)
const _contact = ref({})

function contactOptions(contact) {
  let options = [
    {
      label: __('Remove'),
      icon: 'trash-2',
      onClick: () => removeContact(contact.name),
    },
  ]

  if (!contact.is_primary) {
    options.push({
      label: __('Set as Primary Contact'),
      icon: h(SuccessIcon, { class: 'h-4 w-4' }),
      onClick: () => setPrimaryContact(contact.name),
    })
  }

  return options
}

async function addContact(contact) {
  let d = await call('crm.fcrm.doctype.crm_deal.crm_deal.add_contact', {
    deal: props.dealId,
    contact,
  })
  if (d) {
    dealContacts.reload()
    createToast({
      title: __('Contact added'),
      icon: 'check',
      iconClasses: 'text-ink-green-3',
    })
  }
}

async function removeContact(contact) {
  let d = await call('crm.fcrm.doctype.crm_deal.crm_deal.remove_contact', {
    deal: props.dealId,
    contact,
  })
  if (d) {
    dealContacts.reload()
    createToast({
      title: __('Contact removed'),
      icon: 'check',
      iconClasses: 'text-ink-green-3',
    })
  }
}

async function setPrimaryContact(contact) {
  let d = await call('crm.fcrm.doctype.crm_deal.crm_deal.set_primary_contact', {
    deal: props.dealId,
    contact,
  })
  if (d) {
    dealContacts.reload()
    createToast({
      title: __('Primary contact set'),
      icon: 'check',
      iconClasses: 'text-ink-green-3',
    })
  }
}

const dealContacts = createResource({
  url: 'crm.fcrm.doctype.crm_deal.api.get_deal_contacts',
  params: { name: props.dealId },
  cache: ['deal_contacts', props.dealId],
  auto: true,
  transform: (data) => {
    data.forEach((contact) => {
      contact.opened = false
    })
    return data
  },
})

function triggerCall() {
  let primaryContact = dealContacts.data?.find((c) => c.is_primary)
  let mobile_no = primaryContact.mobile_no || null

  if (!primaryContact) {
    errorMessage(__('No primary contact set'))
    return
  }

  if (!mobile_no) {
    errorMessage(__('No mobile number set'))
    return
  }

  makeCall(mobile_no)
}

function updateField(name, value, callback) {
  let annual_revenue_value = 0;
  let probability_value = 0;

  // Ensure 'annual_revenue' and 'probability' fields are processed correctly
  if (name === 'annual_revenue' || name === 'probability') {
    if (name === 'annual_revenue') {
      // When updating 'annual_revenue', parse the value and use the current probability
      annual_revenue_value = value ? parseFloat(value.replace(/[^0-9.-]+/g, '')) : 0;
      probability_value = deal.data.probability ? parseFloat(deal.data.probability.replace(/[^0-9.-]+/g, '')) : 0;
    } else {
      // When updating 'probability', parse the value and use the current annual revenue
      annual_revenue_value = deal.data.annual_revenue ? parseFloat(deal.data.annual_revenue.replace(/[^0-9.-]+/g, '')) : 0;
      probability_value = value ? parseFloat(value.replace(/[^0-9.-]+/g, '')) : 0;
    }

    // Calculate the weighted amount
    const weighted_amount_value = annual_revenue_value * (probability_value / 100);

    // Update the weighted amount first
    updateDeal('weighted_amount', weighted_amount_value, () => {
      deal.data['weighted_amount'] = weighted_amount_value;

      // Update the specified field
      updateDeal(name, value, () => {
        deal.data[name] = value;

        // Execute the callback if provided
        if (callback) callback();
      });
    });
  } else {
    // Update the specified field when not 'annual_revenue' or 'probability'
    updateDeal(name, value, () => {
      deal.data[name] = value;

      // Execute the callback if provided
      if (callback) callback();
    });
  }

  // Call getStatusDetail with the new value
  getStatusDetail(value);
}
async function deleteDeal(name) {
  await call('frappe.client.delete', {
    doctype: 'CRM Deal',
    name,
  })
  router.push({ name: 'Deals' })
}

const activities = ref(null)

function openEmailBox() {
  activities.value.emailBox.show = true
}
</script>
<<<<<<< HEAD
=======

<style scoped>
:deep(.section:has(.section-field.hidden)) {
  display: none;
}
:deep(.section:has(.section-field:not(.hidden))) {
  display: flex;
}
</style>

>>>>>>> origin/Scrum-9-z1
