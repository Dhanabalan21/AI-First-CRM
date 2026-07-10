import {
  configureStore,
  createSlice,
} from "@reduxjs/toolkit";

export const initialForm = {
  hcp_name: "",
  interaction_type: "Meeting",
  interaction_date: "",
  interaction_time: "",
  attendees: "",
  topics_discussed: "",
  materials_shared: "",
  samples_distributed: "",
  sentiment: "Neutral",
  outcomes: "",
  follow_up_actions: "",
  summary: "",
};

const interactionSlice = createSlice({
  name: "interaction",

  initialState: {
    form: {
      ...initialForm,
    },
    lastTool: "",
  },

  reducers: {
    updateField: (state, action) => {
      const { name, value } = action.payload;

      state.form[name] = value;
    },

    setFormData: (state, action) => {
      state.form = {
        ...state.form,
        ...action.payload,
      };
    },

    resetForm: (state) => {
      state.form = {
        ...initialForm,
      };
    },

    setLastTool: (state, action) => {
      state.lastTool = action.payload;
    },
  },
});

export const {
  updateField,
  setFormData,
  resetForm,
  setLastTool,
} = interactionSlice.actions;

export const store = configureStore({
  reducer: {
    interaction: interactionSlice.reducer,
  },
});