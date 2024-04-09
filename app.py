import requests
import pandas as pd
import streamlit as st


URL = "https://marple.research.crossref.org"


examples = {
    "reference-matching": "1. Boucher RC (2004) New concepts of the pathogenesis of cystic fibrosis lung disease. Eur Resp J 23: 146–158.",
    "preprint-matching": '{"title": ["Functional single-cell genomics of human cytomegalovirus infection"], "issued": {"date-parts": [[2021, 10, 25]]}, "author": [{"given": "Marco Y.", "family": "Hein"}, {"given": "Jonathan S.", "family": "Weissman", "ORCID": "http://orcid.org/0000-0003-2445-670X"}]}',
    "affiliation-matching": "Department of Molecular Medicine, Sapporo Medical University, Sapporo 060-8556, Japan",
}


@st.cache_data(show_spinner=False)
def load_tasks():
    tasks = requests.get(f"{URL}/tasks").json()["message"]["items"]
    return [t["id"] for t in tasks]


@st.cache_data(show_spinner=False)
def load_strategies(task):
    strategies = requests.get(f"{URL}/tasks/{task}/strategies").json()["message"][
        "items"
    ]
    strategies = [(s["id"], s["description"]) for s in strategies if s["default"]] + [
        (s["id"], s["description"]) for s in strategies if not s["default"]
    ]
    return strategies


def clear_text():
    st.session_state["input"] = ""


def matching_view(task):
    print("matching view")
    st.title(task)
    strategies = load_strategies(task)

    strategy = st.selectbox(
        "Choose strategy:", options=strategies, format_func=lambda x: f"{x[0]} ({x[1]})"
    )
    input = st.text_input("Input:", "", key="input")
    if task in examples:
        st.write("Example input:")
        st.markdown(f"```{examples[task]}```")
    submit = st.button("Match")

    if submit:
        with st.spinner("Matching..."):
            data = requests.get(
                f"{URL}/match", {"task": task, "strategy": strategy[0], "input": input}
            ).json()["message"]["items"]
        if data:
            table_data = []
            for record in data:
                table_data.append(
                    {"Matched ID": record["id"], "Confidence": record["confidence"]}
                )
            df = pd.DataFrame(table_data)
            markdown_table = df.to_markdown(index=False)
            st.markdown(markdown_table, unsafe_allow_html=True)
        else:
            st.markdown("No matches found")


def main():
    st.sidebar.title("Matching tasks")

    state = st.session_state
    tasks = load_tasks()

    if "current_view" not in state:
        state["current_view"] = "reference-matching"
    for task in tasks:
        if st.sidebar.button(task, on_click=clear_text):
            state["current_view"] = task
    matching_view(state["current_view"])


if __name__ == "__main__":
    main()
