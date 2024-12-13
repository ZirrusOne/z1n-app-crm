<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Campaigns" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="campaignsListView?.customListActions"
        :actions="campaignsListView.customListActions"
      />
      <Button
        variant="solid"
        :label="__('Create')"
        @click="showDealModal = true"
      >
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </template>
  </LayoutHeader>
  <ViewControls
    ref="viewControls"
    v-model="deals"
    v-model:loadMore="loadMore"
    @updateCrmCustomData="updateCrmCustomData"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="CRM Deal"
    :options="{
      allowedViews: ['list'],
    }"
  />


  <CampaignsListView
    ref="campaignsListView"
    v-if="deals.data && rows.length"
    v-model="deals.data.page_length_count"
    v-model:list="deals"
    :rows="rows"
    :columns="deals.data.columns"
    :options="{
      showTooltip: true,
      resizeColumn: true,
      rowCount: deals.data.row_count,
      totalCount: deals.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @applyFilter="(data) => viewControls.applyFilter(data)"
    @applyDefaultStatusFilter="(value) => viewControls.applyDefaultStatusFilter(value)"
    @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
    @likeDoc="(data) => viewControls.likeDoc(data)"
  />
  <div v-else-if="deals.data" class="flex h-full items-center justify-center">
    <div
      class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500"
    >
      <DealsIcon class="h-10 w-10" />
      <span>{{ __('No {0} Found', [__('Campaigns')]) }}</span>
      <Button :label="__('Create')" @click="showDealModal = true">
        <template #prefix><FeatherIcon name="plus" class="h-4" /></template>
      </Button>
    </div>
  </div>
  <CampaignModal
    v-if="showDealModal"
    v-model="showDealModal"
    v-model:quickEntry="showQuickEntryModal"
    :defaults="defaults"
  />
  <NoteModal
    v-if="showNoteModal"
    v-model="showNoteModal"
    :note="note"
    doctype="CRM Deal"
    :doc="docname"
  />
  <TaskModal
    v-if="showTaskModal"
    v-model="showTaskModal"
    :task="task"
    doctype="CRM Deal"
    :doc="docname"
  />
  <QuickEntryModal
    v-if="showQuickEntryModal"
    v-model="showQuickEntryModal"
    doctype="CRM Deal"
  />
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import CustomActions from '@/components/CustomActions.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import DealsIcon from '@/components/Icons/DealsIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import CampaignModal from '@/components/Modals/CampaignModal.vue'
import NoteModal from '@/components/Modals/NoteModal.vue'
import TaskModal from '@/components/Modals/TaskModal.vue'
import QuickEntryModal from '@/components/Modals/QuickEntryModal.vue'
import ViewControls from '@/components/ViewControls.vue'
import { globalStore } from '@/stores/global'
import { usersStore } from '@/stores/users'
import { organizationsStore } from '@/stores/organizations'
import { statusesStore } from '@/stores/statuses'
import { callEnabled } from '@/composables/settings'
import {
  dateFormat,
  dateTooltipFormat,
  timeAgo,
  website,
  customFormatNumberIntoCurrency,
  formatTime,
} from '@/utils'
import { useRoute } from 'vue-router'
import { ref, reactive, computed, h } from 'vue'
import CampaignsListView from '../components/ListViews/CampaignsListView.vue'

const { makeCall } = globalStore()
const { getUser } = usersStore()
const { getOrganization } = organizationsStore()
const { getDealStatus } = statusesStore()

const route = useRoute()

const campaignsListView = ref(null)
const showDealModal = ref(false)
const showQuickEntryModal = ref(false)

const defaults = reactive({})

// deals data is loaded in the ViewControls component
const deals = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)
const crmColumns = ref()
const crmResults = ref()

// onMounted(async () => {
//   // console.log(crm_columns);
  
// });
function updateCrmCustomData(data) {
  if(data){
    crmColumns.value = transformToColumn(data.keys);
    crmResults.value = transformToResult(data.values, data.keys)
  }
  else{
    crmColumns.value = ''
    crmResults.value = ''
  }

}
function getRow(name, field) {
  function getValue(value) {
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      return value
    }
    return { label: value }
  }
  return getValue(rows.value?.find((row) => row.name == name)[field])
}

// Rows
const rows = computed(() => {
  if (!deals.value?.data?.data){
    return []
  } 
  else{
    return parseRows(deals.value?.data.data)
  }
})

function parseRows(rows) {
  return rows.map((deal) => {
    let _rows = {}
    deals.value.data.rows.forEach((row) => {
      _rows[row] = deal[row]

      if (row == 'organization') {
        _rows[row] = {
          label: deal.organization,
          logo: getOrganization(deal.organization)?.organization_logo,
        }
      } else if (row === 'website') {
        _rows[row] = website(deal.website)
      } else if (row === 'deal_elements') {
        _rows[row] = {
          data: getAllDealElementNames(deal.child_tables?.deal_elements)
        } 
      } else if (row == 'annual_revenue') {
        _rows[row] = customFormatNumberIntoCurrency(
          deal.annual_revenue,
          deal.currency,
        )
      } else if (row == 'weighted_amount') {
        _rows[row] = customFormatNumberIntoCurrency(
          deal.weighted_amount,
          deal.currency,
        )
      } else if (row == 'probability') {
        _rows[row] = deal[row] + '%';
      } else if (row == 'status') {
        _rows[row] = {
          label: deal.status,
          color: getDealStatus(deal.status)?.iconColorClass,
        }
      } else if (row == 'sla_status') {
        let value = deal.sla_status
        let tooltipText = value
        let color =
          deal.sla_status == 'Failed'
            ? 'red'
            : deal.sla_status == 'Fulfilled'
              ? 'green'
              : 'orange'
        if (value == 'First Response Due') {
          value = __(timeAgo(deal.response_by))
          tooltipText = dateFormat(deal.response_by, dateTooltipFormat)
          if (new Date(deal.response_by) < new Date()) {
            color = 'red'
          }
        }
        _rows[row] = {
          label: tooltipText,
          value: value,
          color: color,
        }
      } else if (row == 'deal_owner') {
        _rows[row] = {
          label: deal.deal_owner && getUser(deal.deal_owner).full_name,
          ...(deal.deal_owner && getUser(deal.deal_owner)),
        }
      } else if (row == '_assign') {
        let assignees = JSON.parse(deal._assign || '[]')
        if (!assignees.length && deal.deal_owner) {
          assignees = [deal.deal_owner]
        }
        _rows[row] = assignees.map((user) => ({
          name: user,
          image: getUser(user).user_image,
          label: getUser(user).full_name,
        }))
      } else if (['modified', 'creation'].includes(row)) {
        _rows[row] = {
          label: dateFormat(deal[row], dateTooltipFormat),
          timeAgo: __(timeAgo(deal[row])),
        }
      } else if (
        ['first_response_time', 'first_responded_on', 'response_by'].includes(
          row,
        )
      ) {
        let field = row == 'response_by' ? 'response_by' : 'first_responded_on'
        _rows[row] = {
          label: deal[field] ? dateFormat(deal[field], dateTooltipFormat) : '',
          timeAgo: deal[row]
            ? row == 'first_response_time'
              ? formatTime(deal[row])
              : __(timeAgo(deal[row]))
            : '',
        }
      }
    })
    _rows['_email_count'] = deal._email_count
    _rows['_note_count'] = deal._note_count
    _rows['_task_count'] = deal._task_count
    _rows['_comment_count'] = deal._comment_count
    return _rows
  })
}

function onNewClick(column) {
  let column_field = deals.value.params.column_field

  if (column_field) {
    defaults[column_field] = column.column.name
  }

  showDealModal.value = true
}


function actions(itemName) {
  let mobile_no = getRow(itemName, 'mobile_no')?.label || ''
  let actions = [
    {
      icon: h(PhoneIcon, { class: 'h-4 w-4' }),
      label: __('Make a Call'),
      onClick: () => makeCall(mobile_no),
      condition: () => mobile_no && callEnabled.value,
    },
    {
      icon: h(NoteIcon, { class: 'h-4 w-4' }),
      label: __('New Note'),
      onClick: () => showNote(itemName),
    },
    {
      icon: h(TaskIcon, { class: 'h-4 w-4' }),
      label: __('New Task'),
      onClick: () => showTask(itemName),
    },
  ]
  return actions.filter((action) =>
    action.condition ? action.condition() : true,
  )
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

/**
 * Get deal elamenet and convert into array
 * @param deals 
 */
function getAllDealElementNames(deals) {
  deals = unwrapProxy(deals);
    // Check if deals is an array
    if (deals && !Array.isArray(deals)) {
        return '';
    }
    return deals;
}

const docname = ref('')
const showNoteModal = ref(false)
const note = ref({
  title: '',
  content: '',
})

function showNote(name) {
  docname.value = name
  showNoteModal.value = true
}

const showTaskModal = ref(false)
const task = ref({
  title: '',
  description: '',
  assigned_to: '',
  due_date: '',
  priority: 'Low',
  status: 'Backlog',
})

function showTask(name) {
  docname.value = name
  showTaskModal.value = true
}

function transformToResult(data, columns) {
  return data.map(row => {
        const obj = {};
        
        // Iterate over columns and map data to corresponding field using the index
        columns.forEach((column, index) => {
            const value = row[index];
            obj[column] = value; // Directly map the value to the column name
        });
        
        return obj;
    });
}

function transformToColumn(test) {
  return test.map(item => ({
        label: item.charAt(0).toUpperCase() + item.slice(1).replace(/_/g, ' '), // Capitalize first letter and replace underscores with spaces
        fieldname: item,
        fieldtype: "Data",
        width: item === "lead_name" ? 100 : 180 // Example of custom width based on the fieldname
    }));
}
</script>
