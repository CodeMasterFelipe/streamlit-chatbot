import streamlit as st
import requests
import replicate

# Set the SDXL API endpoint
api_endpoint = "https://api.replicate.ai/samples/sdxl"

# Define the Streamlit app


def main():
    st.title("Create AI Art with SDXL")
    st.write(
        "Enter your text below and click the 'Generate Art' button to create AI-generated art.")

    # Get user input
    text_input = st.text_input("Enter text", "")

    # Generate AI art
    if st.button("Generate Art"):
        if text_input:
            # Make API request
            output = replicate.run(
                "stability-ai/sdxl:8beff3369e81422112d93b89ca01426147de542cd4684c244b673b105188fe5f",
                input={
                    "prompt": text_input,
                    "width": 1024,
                    "height": 1024,
                    "num_inference_steps": 30,
                    "scheduler": 'DDIM',
                    "guidance_scale": 7.5,
                    "refine": 'expert_ensemble_refiner',
                    "high_noise_frac": 0.8,
                    "refine_steps": 20,
                },
            )

            print(output)

            st.image(output, caption="AI Art")
            # else:
            #     st.error("Failed to generate AI art. Please try again.")
        else:
            st.warning("Please enter some text.")


# Run the Streamlit app
if __name__ == "__main__":
    main()
