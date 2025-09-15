import os
import torch  # Explicitly import torch to fix UnboundLocalError
from dotenv import load_dotenv
from diffusers import StableDiffusionPipeline, AutoencoderKL
from llm_agent import generate_three_outfits_mistral

load_dotenv()

# Debug: Print token if present
print("HUGGINGFACE_TOKEN:", os.environ.get("HUGGINGFACE_TOKEN")[:10] + "..." if os.environ.get("HUGGINGFACE_TOKEN") else "None")

def generate_images_for_outfits(outfit_descriptions):
    """
    Generate images from Stable Diffusion locally using Hugging Face diffusers.

    Args:
        outfit_descriptions (list[str]): List of outfit prompts/text descriptions.

    Returns:
        list of dict: Each with 'description' and local image file path.
    """

    # Use CPU or MPS (Apple Silicon Metal Performance Shaders) on M1/M2 Macs
    if torch.backends.mps.is_available():
        device = "mps"
        torch_device = torch.device("mps")
    else:
        device = "cpu"
        torch_device = torch.device("cpu")
    print(f"Using device: {device}")

    try:
        # Load VAE for better quality
        vae = AutoencoderKL.from_pretrained(
            "stabilityai/sd-vae-ft-mse-original",
            torch_dtype=torch.float16 if torch.backends.mps.is_available() else torch.float32
        )

        pipeline = StableDiffusionPipeline.from_pretrained(
            "SG161222/Realistic_Vision_V2.0",  # Corrected repo ID
            torch_dtype=torch.float16 if torch.backends.mps.is_available() else torch.float32,
            vae=vae
        )
        print("Model loaded: SG161222/Realistic_Vision_V2.0")
    except Exception as e:
        print(f"Failed to load Realistic Vision model: {e}")
        # Fallback to a public Stable Diffusion model
        try:
            pipeline = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float16 if torch.backends.mps.is_available() else torch.float32
            )
            print("Loaded fallback model: runwayml/stable-diffusion-v1-5")
        except Exception as fallback_e:
            raise RuntimeError(f"Failed to load fallback model: {fallback_e}")

    pipeline = pipeline.to(torch_device)

    results = []

    save_dir = os.path.join(os.getcwd(), "generation")
    os.makedirs(save_dir, exist_ok=True)

    for i, desc in enumerate(outfit_descriptions, start=1):
        try:
            # Enhance prompt for better image quality
            prompt = f"Realistic photo of {desc}, high quality, detailed, natural lighting, elegant female attire"
            image = pipeline(prompt, guidance_scale=7.5).images[0]
            filename = os.path.join(save_dir, f"outfit_{i}.png")
            image.save(filename)
            results.append({"description": desc, "image_path": filename})
            print(f"Generated Outfit {i}: {desc[:50]}...")
        except Exception as e:
            results.append({"description": desc, "error": str(e)})
            print(f"Error generating Outfit {i}: {e}")

    return results


# Example usage:
if __name__ == "__main__":
    from llm_agent import generate_three_outfits_mistral

    event_details = {
        "date": "2025-10-10",
        "event_type": "wedding",
        "gender": "female",
        "weather": "cool, windy evening, 18°C",
        "location": "London, outdoor venue",
        "time": "evening",
        "occasion": "semi-formal business gala",
        "vibe": "professional, elegant",
        "dress_code": None
    }
    detail=generate_three_outfits_mistral(event_details)

    outfit_json = generate_three_outfits_mistral(detail)
    descriptions = [o["description"] for o in outfit_json.get("outfits", [])]

    images = generate_images_for_outfits(descriptions)

    for idx, img in enumerate(images, 1):
        if "image_path" in img:
            print(f"Outfit {idx} image saved at: {img['image_path']}")
        else:
            print(f"Outfit {idx} error: {img.get('error', 'Unknown error')}")