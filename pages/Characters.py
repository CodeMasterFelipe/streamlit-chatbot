import streamlit as st
import streamlit.components.v1 as components
from streamlit_extras.no_default_selectbox import selectbox
import os
from db.database import Database


class CharactersPage():

    def __init__(self):
        self.save_image_dir = "db/images"
        self.new_character_placeholder = "+ New Character"
        self.saved_image_extesion = "png"

        self.initialize_state()

    def initialize_state(self):
        if "db" not in st.session_state:
            st.session_state["db"] = Database()

    def save_image(self, filename, content):
        with open(os.path.join(self.save_image_dir, filename), "wb") as f:
            f.write(content)

    def load_image(self, filename):
        if not filename:
            return []

        try:
            with open(os.path.join(self.save_image_dir, filename), "rb") as f:
                return f.read()
        except IOError as e:
            return []

    def handle_new_character(self):
        print(st.session_state.character_selected)
        st.session_state.character_selected = self.new_character_placeholder

    # this will failed when changing "name"
    def handle_save_character(self, **settings):
        is_image_uploaded = settings.pop("uploaded_file")
        image_content = settings.pop("image_content")
        if is_image_uploaded:
            self.save_image(
                settings["name"] + "." + self.saved_image_extesion, image_content)

        if st.session_state.character_selected != self.new_character_placeholder:
            st.session_state.db.update_character(settings)
        else:
            st.session_state.db.insert_character(settings)

    def settings(self):

        char_info = {}
        selected_char_name = st.session_state.character_selected
        if selected_char_name == self.new_character_placeholder:
            selected_char_name = ""
        else:
            char_info = st.session_state.db.get_character(selected_char_name)

        name = st.text_input("Name", selected_char_name)

        uploaded_file = st.file_uploader("avatar image",  ['png', 'jpg'])
        if uploaded_file:
            image_data = uploaded_file.read()
            # bytes_data = uploaded_file.read()
            st.write("Filename:", uploaded_file.name)
        else:
            image_data = self.load_image(
                selected_char_name + "." + self.saved_image_extesion)

        st.image(image_data, width=100)

        system_prompt = st.text_area(
            "System Prompt", char_info.get("system_prompt", ""))
        temperature = st.slider("Temperature", min_value=0.0, max_value=5.0,
                                value=float(char_info.get("temperature", 1.0)))

        st.button("Save Settings", type="primary", on_click=self.handle_save_character, kwargs={
            "uploaded_file": uploaded_file,
            "image_content": image_data,
            "name": name,
            "system_prompt": system_prompt,
            "temperature": temperature,
        })

    def run(self):
        st.title("Character Customization")
        col1, col2 = st.columns([0.8, .20])
        # col1.selectbox("Select Character", [
        #                "Nova", "AI Artist"], key="character_selected")
        with col1:
            selectbox("Select Character", st.session_state.db.get_all_characters(
            ), index=0, no_selection_label=self.new_character_placeholder, key="character_selected")
        col2.button("new character", type="secondary",
                    use_container_width=True, on_click=self.handle_new_character)

        self.settings()


st.write(
    """<style>
    [data-testid="stHorizontalBlock"] {
        align-items: end;
    }
    </style>
    """,
    unsafe_allow_html=True
)
CharactersPage().run()
