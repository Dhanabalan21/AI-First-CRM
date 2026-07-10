import {
  useEffect,
  useMemo,
  useState,
} from "react";

import axios from "axios";

import {
  useDispatch,
  useSelector,
} from "react-redux";

import {
  resetForm,
  setFormData,
  setLastTool,
  updateField,
} from "./store";

import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const dispatch = useDispatch();

  const form = useSelector(
    (state) => state.interaction.form
  );

  const lastTool = useSelector(
    (state) => state.interaction.lastTool
  );

  const [interactions, setInteractions] =
    useState([]);

  const [message, setMessage] =
    useState("");

  const [chat, setChat] =
    useState([]);

  const [search, setSearch] =
    useState("");

  const [
    sentimentFilter,
    setSentimentFilter,
  ] = useState("");

  const [darkMode, setDarkMode] =
    useState(false);

  const [loading, setLoading] =
    useState(false);

  const [saving, setSaving] =
    useState(false);

  const [status, setStatus] = useState({
    type: "",
    message: "",
  });

  const metrics = useMemo(() => {
    const positive =
      interactions.filter(
        (item) =>
          item.sentiment === "Positive"
      ).length;

    const followUps =
      interactions.filter(
        (item) =>
          item.follow_up_actions?.trim()
      ).length;

    const meetings =
      interactions.filter(
        (item) =>
          item.interaction_type ===
          "Meeting"
      ).length;

    return {
      total: interactions.length,
      positive,
      followUps,
      meetings,
    };
  }, [interactions]);

  const sentimentPercentages =
    useMemo(() => {
      const total =
        interactions.length || 1;

      const count = (name) =>
        interactions.filter(
          (item) =>
            item.sentiment === name
        ).length;

      return {
        Positive: Math.round(
          (count("Positive") / total) *
            100
        ),

        Neutral: Math.round(
          (count("Neutral") / total) *
            100
        ),

        Negative: Math.round(
          (count("Negative") / total) *
            100
        ),
      };
    }, [interactions]);

  const showStatus = (
    type,
    text
  ) => {
    setStatus({
      type,
      message: text,
    });

    window.setTimeout(() => {
      setStatus({
        type: "",
        message: "",
      });
    }, 3500);
  };

  const handleChange = (event) => {
    dispatch(
      updateField({
        name: event.target.name,
        value: event.target.value,
      })
    );
  };

  const loadInteractions =
    async () => {
      try {
        const response =
          await axios.get(
            `${API_URL}/api/interactions`,
            {
              params: {
                search,
                sentiment:
                  sentimentFilter,
              },
            }
          );

        setInteractions(
          response.data
        );
      } catch {
        showStatus(
          "error",
          "Unable to load interactions."
        );
      }
    };

  const sendMessage = async () => {
    if (!message.trim()) {
      showStatus(
        "error",
        "Enter a message first."
      );

      return;
    }

    const userMessage =
      message.trim();

    setChat((current) => [
      ...current,
      {
        role: "user",
        text: userMessage,
      },
    ]);

    setLoading(true);

    try {
      const response =
        await axios.post(
          `${API_URL}/api/agent/chat`,
          {
            message: userMessage,
          }
        );

      const data = response.data;

      dispatch(
        setLastTool(
          data.tool || ""
        )
      );

      if (data.interaction_data) {
        dispatch(
          setFormData(
            data.interaction_data
          )
        );
      }

      if (data.interaction) {
        dispatch(
          setFormData(
            data.interaction
          )
        );
      }

      let assistantText =
        data.message ||
        "Request completed.";

      if (data.error) {
        assistantText =
          data.error;
      }

      if (data.suggestions) {
        assistantText =
          data.suggestions;
      }

      if (
        data.tool ===
        "list_interactions"
      ) {
        assistantText =
          data.interactions?.length
            ? data.interactions
                .map(
                  (item) =>
                    `#${item.id} · ${item.hcp_name} · ${item.sentiment}`
                )
                .join("\n")
            : "No interactions found.";
      }

      setChat((current) => [
        ...current,
        {
          role: "assistant",
          text: assistantText,
          tool: data.tool,
        },
      ]);

      setMessage("");

      if (
        data.tool ===
          "edit_interaction" ||
        data.tool ===
          "list_interactions"
      ) {
        await loadInteractions();
      }
    } catch (error) {
      const text =
        error.response?.data
          ?.detail ||
        "Unable to contact the AI service.";

      setChat((current) => [
        ...current,
        {
          role: "assistant",
          text,
        },
      ]);

      showStatus(
        "error",
        text
      );
    } finally {
      setLoading(false);
    }
  };

  const saveInteraction =
    async () => {
      if (
        !form.hcp_name.trim()
      ) {
        showStatus(
          "error",
          "HCP name is required."
        );

        return;
      }

      setSaving(true);

      try {
        await axios.post(
          `${API_URL}/api/interactions`,
          form
        );

        showStatus(
          "success",
          "Interaction saved successfully."
        );

        dispatch(resetForm());
        dispatch(setLastTool(""));

        await loadInteractions();
      } catch (error) {
        showStatus(
          "error",
          error.response?.data
            ?.detail ||
            "Unable to save interaction."
        );
      } finally {
        setSaving(false);
      }
    };

  const deleteInteraction =
    async (id) => {
      const confirmed =
        window.confirm(
          `Delete interaction ${id}?`
        );

      if (!confirmed) {
        return;
      }

      try {
        await axios.delete(
          `${API_URL}/api/interactions/${id}`
        );

        showStatus(
          "success",
          "Interaction deleted."
        );

        await loadInteractions();
      } catch {
        showStatus(
          "error",
          "Unable to delete interaction."
        );
      }
    };

  const loadIntoForm = (
    item
  ) => {
    dispatch(
      setFormData(item)
    );

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const exportCsv = () => {
    if (
      !interactions.length
    ) {
      showStatus(
        "error",
        "No interactions to export."
      );

      return;
    }

    const headers = [
      "ID",
      "HCP Name",
      "Type",
      "Date",
      "Sentiment",
      "Topics",
      "Outcome",
      "Follow-up",
    ];

    const rows =
      interactions.map(
        (item) => [
          item.id,
          item.hcp_name,
          item.interaction_type,
          item.interaction_date,
          item.sentiment,
          item.topics_discussed,
          item.outcomes,
          item.follow_up_actions,
        ]
      );

    const csv = [
      headers,
      ...rows,
    ]
      .map((row) =>
        row
          .map(
            (cell) =>
              `"${String(
                cell ?? ""
              ).replaceAll(
                '"',
                '""'
              )}"`
          )
          .join(",")
      )
      .join("\n");

    const blob = new Blob(
      [csv],
      {
        type:
          "text/csv;charset=utf-8",
      }
    );

    const url =
      URL.createObjectURL(blob);

    const anchor =
      document.createElement(
        "a"
      );

    anchor.href = url;

    anchor.download =
      "hcp-interactions.csv";

    anchor.click();

    URL.revokeObjectURL(url);
  };

  useEffect(() => {
    loadInteractions();
  }, []);

  return (
    <div
      className={
        darkMode
          ? "app dark"
          : "app"
      }
    >
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            AI
          </div>

          <div>
            <strong>
              HCP CRM
            </strong>

            <span>
              Life Sciences
            </span>
          </div>
        </div>

        <nav>
          <button className="nav-item active">
            Dashboard
          </button>

          <button className="nav-item">
            Interactions
          </button>

          <button className="nav-item">
            AI Assistant
          </button>

          <button className="nav-item">
            Reports
          </button>

          <button className="nav-item">
            Settings
          </button>
        </nav>

        <div className="sidebar-footer">
          <span>
            Powered by
          </span>

          <strong>
            LangGraph · Groq
          </strong>
        </div>
      </aside>

      <div className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">
              AI-FIRST CRM
            </p>

            <h1>
              Healthcare Professional CRM
            </h1>

            <p>
              Manage interactions,
              follow-ups, and HCP
              engagement.
            </p>
          </div>

          <div className="topbar-actions">
            <button
              className="ghost-button"
              onClick={exportCsv}
            >
              Export CSV
            </button>

            <button
              className="ghost-button"
              onClick={() =>
                setDarkMode(
                  (value) =>
                    !value
                )
              }
            >
              {darkMode
                ? "Light Mode"
                : "Dark Mode"}
            </button>

            <div className="profile">
              DS
            </div>
          </div>
        </header>

        {status.message && (
          <div
            className={`status ${status.type}`}
          >
            {status.message}
          </div>
        )}

        <section className="metrics">
          <article className="metric-card">
            <span>
              Total Interactions
            </span>

            <strong>
              {metrics.total}
            </strong>

            <small>
              All recorded HCP
              activities
            </small>
          </article>

          <article className="metric-card">
            <span>
              Positive Sentiment
            </span>

            <strong>
              {metrics.positive}
            </strong>

            <small>
              Engaged HCP
              conversations
            </small>
          </article>

          <article className="metric-card">
            <span>
              Follow-ups Pending
            </span>

            <strong>
              {metrics.followUps}
            </strong>

            <small>
              Actions requiring
              attention
            </small>
          </article>

          <article className="metric-card">
            <span>
              Meetings
            </span>

            <strong>
              {metrics.meetings}
            </strong>

            <small>
              Face-to-face
              interactions
            </small>
          </article>
        </section>

        <section className="main-grid">
          <article className="card form-card">
            <div className="card-heading">
              <div>
                <h2>
                  Log HCP Interaction
                </h2>

                <p>
                  Enter details manually
                  or populate them through
                  AI.
                </p>
              </div>

              <span className="section-tag">
                Structured Form
              </span>
            </div>

            <div className="form-grid">
              <label>
                HCP Name

                <input
                  name="hcp_name"
                  value={
                    form.hcp_name
                  }
                  onChange={
                    handleChange
                  }
                  placeholder="Dr. Smith"
                />
              </label>

              <label>
                Interaction Type

                <select
                  name="interaction_type"
                  value={
                    form.interaction_type
                  }
                  onChange={
                    handleChange
                  }
                >
                  <option>
                    Meeting
                  </option>

                  <option>
                    Phone Call
                  </option>

                  <option>
                    Email
                  </option>

                  <option>
                    Virtual Meeting
                  </option>

                  <option>
                    Conference
                  </option>

                  <option>
                    Other
                  </option>
                </select>
              </label>

              <label>
                Date

                <input
                  type="date"
                  name="interaction_date"
                  value={
                    form.interaction_date
                  }
                  onChange={
                    handleChange
                  }
                />
              </label>

              <label>
                Time

                <input
                  type="time"
                  name="interaction_time"
                  value={
                    form.interaction_time
                  }
                  onChange={
                    handleChange
                  }
                />
              </label>

              <label className="span-2">
                Attendees

                <input
                  name="attendees"
                  value={
                    form.attendees
                  }
                  onChange={
                    handleChange
                  }
                  placeholder="Enter attendee names"
                />
              </label>

              <label className="span-2">
                Topics Discussed

                <textarea
                  name="topics_discussed"
                  value={
                    form.topics_discussed
                  }
                  onChange={
                    handleChange
                  }
                  placeholder="Discussion topics"
                />
              </label>

              <label>
                Materials Shared

                <input
                  name="materials_shared"
                  value={
                    form.materials_shared
                  }
                  onChange={
                    handleChange
                  }
                  placeholder="Clinical brochure"
                />
              </label>

              <label>
                Samples Distributed

                <input
                  name="samples_distributed"
                  value={
                    form.samples_distributed
                  }
                  onChange={
                    handleChange
                  }
                  placeholder="Product sample"
                />
              </label>

              <label>
                Sentiment

                <select
                  name="sentiment"
                  value={
                    form.sentiment
                  }
                  onChange={
                    handleChange
                  }
                >
                  <option>
                    Positive
                  </option>

                  <option>
                    Neutral
                  </option>

                  <option>
                    Negative
                  </option>
                </select>
              </label>

              <label>
                Outcome

                <input
                  name="outcomes"
                  value={
                    form.outcomes
                  }
                  onChange={
                    handleChange
                  }
                  placeholder="Requested a brochure"
                />
              </label>

              <label className="span-2">
                Follow-Up Actions

                <textarea
                  name="follow_up_actions"
                  value={
                    form.follow_up_actions
                  }
                  onChange={
                    handleChange
                  }
                  placeholder="Schedule a follow-up meeting"
                />
              </label>

              <label className="span-2">
                Summary

                <textarea
                  name="summary"
                  value={
                    form.summary
                  }
                  onChange={
                    handleChange
                  }
                  placeholder="Professional summary"
                />
              </label>
            </div>

            <div className="form-actions">
              <button
                className="primary-button"
                onClick={
                  saveInteraction
                }
                disabled={saving}
              >
                {saving
                  ? "Saving..."
                  : "Save Interaction"}
              </button>

              <button
                className="ghost-button"
                onClick={() =>
                  dispatch(
                    resetForm()
                  )
                }
              >
                Clear Form
              </button>
            </div>
          </article>

          <article className="card assistant-card">
            <div className="card-heading">
              <div>
                <h2>
                  AI Assistant
                </h2>

                <p>
                  Use natural language
                  to manage HCP
                  interactions.
                </p>
              </div>

              <span className="section-tag">
                {lastTool ||
                  "Ready"}
              </span>
            </div>

            <div className="chat-window">
              {!chat.length && (
                <div className="empty-chat">
                  <div className="assistant-icon">
                    AI
                  </div>

                  <h3>
                    How can I help?
                  </h3>

                  <p>
                    Describe an HCP
                    interaction or ask me
                    to list, edit, or
                    suggest follow-up
                    actions.
                  </p>
                </div>
              )}

              {chat.map(
                (item, index) => (
                  <div
                    className={`message ${item.role}`}
                    key={`${item.role}-${index}`}
                  >
                    <span>
                      {item.role ===
                      "user"
                        ? "You"
                        : "AI"}
                    </span>

                    <p>
                      {item.text}
                    </p>
                  </div>
                )
              )}

              {loading && (
                <div className="message assistant">
                  <span>
                    AI
                  </span>

                  <p>
                    Thinking...
                  </p>
                </div>
              )}
            </div>

            <div className="quick-actions">
              <button
                onClick={() =>
                  setMessage(
                    "List all interactions"
                  )
                }
              >
                List interactions
              </button>

              <button
                onClick={() =>
                  setMessage(
                    "Show interaction 1"
                  )
                }
              >
                Show #1
              </button>

              <button
                onClick={() =>
                  setMessage(
                    "Edit interaction 1 sentiment to Neutral"
                  )
                }
              >
                Edit #1
              </button>

              <button
                onClick={() =>
                  setMessage(
                    "Suggest follow-up for Dr. Smith"
                  )
                }
              >
                Suggest follow-up
              </button>
            </div>

            <div className="composer">
              <textarea
                value={message}
                onChange={(event) =>
                  setMessage(
                    event.target.value
                  )
                }
                placeholder="Describe the interaction..."
              />

              <button
                onClick={
                  sendMessage
                }
                disabled={loading}
              >
                Send
              </button>
            </div>
          </article>
        </section>

        <section className="analytics-grid">
          <article className="card">
            <div className="card-heading">
              <div>
                <h2>
                  Sentiment Overview
                </h2>

                <p>
                  Engagement quality
                  across recorded
                  interactions.
                </p>
              </div>
            </div>

            {Object.entries(
              sentimentPercentages
            ).map(
              ([name, value]) => (
                <div
                  className="bar-row"
                  key={name}
                >
                  <div>
                    <span>
                      {name}
                    </span>

                    <strong>
                      {value}%
                    </strong>
                  </div>

                  <div className="bar-track">
                    <div
                      className={`bar-fill ${name.toLowerCase()}`}
                      style={{
                        width: `${value}%`,
                      }}
                    />
                  </div>
                </div>
              )
            )}
          </article>

          <article className="card suggestion-card">
            <div className="card-heading">
              <div>
                <h2>
                  AI Suggestions
                </h2>

                <p>
                  Recommended daily
                  actions for field
                  representatives.
                </p>
              </div>
            </div>

            <div className="suggestion-item">
              <span>1</span>
              Review pending HCP
              follow-up actions.
            </div>

            <div className="suggestion-item">
              <span>2</span>
              Share clinical material
              requested during meetings.
            </div>

            <div className="suggestion-item">
              <span>3</span>
              Prioritize HCPs with
              positive engagement.
            </div>
          </article>
        </section>

        <section className="card table-card">
          <div className="table-header">
            <div>
              <h2>
                Recent Interactions
              </h2>

              <p>
                Search, filter, review,
                or delete interaction
                records.
              </p>
            </div>

            <div className="filters">
              <input
                value={search}
                onChange={(event) =>
                  setSearch(
                    event.target.value
                  )
                }
                placeholder="Search HCP or topic"
              />

              <select
                value={
                  sentimentFilter
                }
                onChange={(event) =>
                  setSentimentFilter(
                    event.target.value
                  )
                }
              >
                <option value="">
                  All sentiments
                </option>

                <option>
                  Positive
                </option>

                <option>
                  Neutral
                </option>

                <option>
                  Negative
                </option>
              </select>

              <button
                onClick={
                  loadInteractions
                }
              >
                Apply
              </button>
            </div>
          </div>

          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>HCP</th>
                  <th>Type</th>
                  <th>
                    Sentiment
                  </th>
                  <th>Date</th>
                  <th>Topic</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {!interactions.length && (
                  <tr>
                    <td
                      colSpan="7"
                      className="empty-row"
                    >
                      No interactions
                      found.
                    </td>
                  </tr>
                )}

                {interactions.map(
                  (item) => (
                    <tr key={item.id}>
                      <td>
                        #{item.id}
                      </td>

                      <td>
                        <strong>
                          {
                            item.hcp_name
                          }
                        </strong>
                      </td>

                      <td>
                        {
                          item.interaction_type
                        }
                      </td>

                      <td>
                        <span
                          className={`sentiment ${item.sentiment.toLowerCase()}`}
                        >
                          {
                            item.sentiment
                          }
                        </span>
                      </td>

                      <td>
                        {item.interaction_date ||
                          "—"}
                      </td>

                      <td>
                        {item.topics_discussed ||
                          "—"}
                      </td>

                      <td>
                        <div className="row-actions">
                          <button
                            onClick={() =>
                              loadIntoForm(
                                item
                              )
                            }
                          >
                            Open
                          </button>

                          <button
                            className="danger"
                            onClick={() =>
                              deleteInteraction(
                                item.id
                              )
                            }
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        </section>

        <footer>
          <span>
            AI-First HCP CRM
          </span>

          <span>
            Developed by Dhanabalan
          </span>
        </footer>
      </div>
    </div>
  );
}

export default App;