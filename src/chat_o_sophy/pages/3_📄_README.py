import streamlit as st

from chat_o_sophy.sidebar import Sidebar

st.set_page_config(page_title="chat-o-sophy - README", page_icon="💭", layout="wide")


def main():
    sidebar = st.session_state.setdefault("sidebar", Sidebar())
    sidebar.main()
    
    st.write("TO BE DONE")


if __name__ == "__main__":
    main()
