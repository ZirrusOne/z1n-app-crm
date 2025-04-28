<template>
    <div class="flex gap-2 flex-wrap">
      <div v-if="Array.isArray(deals) && deals.length > 0">
        <div
          v-for="(deal, index) in deals"
          :key="index"
          class="chip rounded-full bg-slate-800 py-0.5 px-2.5 border border-transparent text-sm text-white transition-all shadow-sm"
        >
          {{ deal.deal_elements }}
        </div>
      </div>
    </div>
  </template>

  <script>
  export default {
    props: {
      deals: {
        type: Array,
        default: () => [],
      },
    },
    methods: {
      getElementText(deal) {
        // Only return the deal_elements property
        if (typeof deal === 'object' && deal.deal_elements) {
          return deal.deal_elements;
        }

        // Fallback if deal_elements is not available
        return '';
      }
    }
  };
  </script>