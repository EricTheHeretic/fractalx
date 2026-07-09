import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from hashlib import sha256
import io
import random
from PIL import Image, ImageDraw
from cryptography.fernet import Fernet
import base64

# Phonetic alphabet mapping
PHONETIC = {
    'A': 'Alpha', 'B': 'Bravo', 'C': 'Charlie', 'D': 'Delta', 'E': 'Echo',
    'F': 'Foxtrot', 'G': 'Golf', 'H': 'Hotel', 'I': 'India', 'J': 'Juliett',
    'K': 'Kilo', 'L': 'Lima', 'M': 'Mike', 'N': 'November', 'O': 'Oscar',
    'P': 'Papa', 'Q': 'Quebec', 'R': 'Romeo', 'S': 'Sierra', 'T': 'Tango',
    'U': 'Uniform', 'V': 'Victor', 'W': 'Whiskey', 'X': 'Xray', 'Y': 'Yankee', 'Z': 'Zulu'
}

st.set_page_config(page_title="FractalX", layout="wide")

# ====================== WIDE BANNER ======================
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.markdown("""
        <h1 style='text-align: center; margin-bottom: 5px;'>
            FRACTAL <span style='color: #e0bbff; font-size: 1.4em;'>X</span>
        </h1>
        """, unsafe_allow_html=True)

st.divider()

tab1, tab2 = st.tabs(["✉️ Encode", "🔓 Decode"])

with tab1:
    st.subheader("Message")
    message = st.text_area("Type your secret message", height=70)

    st.subheader("Password for this image")
    passphrase = st.text_input("Create a password", type="password")

    pepe_mode = st.checkbox("🐸 Deploy Pepe (random meme)")
    phonetic_mode = st.checkbox("🔤 Phonetic Geometry Mode")

    if st.button("Generate Fractal + Hide Message", type="primary", use_container_width=True):
        if not message or not passphrase:
            st.error("Please enter a message and password.")
        else:
            key = base64.urlsafe_b64encode(sha256(passphrase.encode()).digest()[:32])
            fernet = Fernet(key)
            encrypted = fernet.encrypt(message.encode())

            if pepe_mode:
                pepe_files = ["pepe1.png", "pepe2.png", "pepe3.png", "pepe4.png", "pepe5.png"]
                chosen = random.choice(pepe_files)
                try:
                    img = Image.open(chosen).convert("RGB")
                except:
                    st.error(f"Could not find {chosen}")
                    st.stop()
            else:
                # Normal fractal
                width, height = 700, 500
                x = np.linspace(-2.5, 1.5, width)
                y = np.linspace(-1.5, 1.5, height)
                X, Y = np.meshgrid(x, y)
                C = X + 1j * Y
                Z = np.zeros_like(C)
                divtime = np.zeros(C.shape, dtype=int)

                for i in range(80):
                    mask = np.abs(Z) <= 2
                    Z[mask] = Z[mask]**2 + C[mask]
                    divtime[mask & (np.abs(Z) > 2)] = i

                fig, ax = plt.subplots(figsize=(8, 5.5))
                ax.imshow(divtime, cmap="inferno", extent=[x.min(), x.max(), y.min(), y.max()])
                ax.axis("off")
                buf = io.BytesIO()
                fig.savefig(buf, format="png", bbox_inches="tight", dpi=120)
                plt.close(fig)
                buf.seek(0)
                img = Image.open(buf).convert("RGB")

            # Phonetic geometry on top (works with both normal and Pepe)
            if phonetic_mode:
                phonetic_msg = ' '.join(PHONETIC.get(c.upper(), c) for c in message if c.isalpha())
                st.info(f"Phonetic sequence hidden: {phonetic_msg[:80]}...")
                draw = ImageDraw.Draw(img)
                # Simple phonetic markers seeded by password
                random.seed(int(sha256(passphrase.encode()).hexdigest(), 16))
                for i in range(min(20, len(phonetic_msg))):
                    x = random.randint(50, img.width-50)
                    y = random.randint(50, img.height-50)
                    draw.text((x, y), phonetic_msg[i], fill=(255, 255, 0), size=20)

            # Hide the message in pixels
            FIXED_SIZE = 256
            data = encrypted.ljust(FIXED_SIZE, b'\0')[:FIXED_SIZE]

            arr = np.array(img)
            flat = arr.reshape(-1, 3)
            random.seed(int(sha256(passphrase.encode()).hexdigest(), 16))
            idx = list(range(len(flat)))
            random.shuffle(idx)

            bits = ''.join(f'{b:08b}' for b in data)
            for i, bit in enumerate(bits):
                if i >= len(idx): break
                p = idx[i]
                flat[p, 0] = (flat[p, 0] & 0xFE) | int(bit)

            final = Image.fromarray(flat.reshape(arr.shape).astype("uint8"))
            out = io.BytesIO()
            final.save(out, format="PNG")

            st.success("✅ Encrypted image created!")
            st.image(out, use_container_width=True)

            col_download, col_share = st.columns(2)
            with col_download:
                st.download_button("⬇️ Download PNG", out.getvalue(), "fractalx.png", "image/png", use_container_width=True)
            with col_share:
                tweet_text = "Secret message hidden inside this fractal. Only the right password can read it. Made with FractalX"
                x_url = f"https://twitter.com/intent/tweet?text={tweet_text}&url=https://fractalx-3fxnxrg2auquemymk5rmxv.streamlit.app"
                st.link_button("📤 Share to X", x_url, use_container_width=True)

with tab2:
    st.subheader("Decode a Fractal Image")
    st.write("Upload the PNG you received, then enter the password.")

    uploaded = st.file_uploader("Upload PNG", type=["png"])
    pw = st.text_input("Password", type="password")

    if st.button("Decode Message", use_container_width=True):
        if uploaded and pw:
            try:
                img = Image.open(uploaded).convert("RGB")
                arr = np.array(img)
                flat = arr.reshape(-1, 3)

                FIXED_SIZE = 256
                random.seed(int(sha256(pw.encode()).hexdigest(), 16))
                idx = list(range(len(flat)))
                random.shuffle(idx)

                bits = [str(flat[idx[i], 0] & 1) for i in range(FIXED_SIZE * 8)]
                bitstr = ''.join(bits)
                raw = bytearray(int(bitstr[i:i+8], 2) for i in range(0, len(bitstr), 8))

                key = base64.urlsafe_b64encode(sha256(pw.encode()).digest()[:32])
                fernet = Fernet(key)
                dec = fernet.decrypt(bytes(raw)).rstrip(b'\0')

                st.success("✅ Message decoded!")
                st.code(dec.decode())
            except Exception as e:
                st.error(f"Decoding failed: {e}")
        else:
            st.warning("Please upload the image and enter the password.")

st.divider()

st.markdown("""
**How it works:**
- Create a message + password → generates a fractal with your message hidden inside the pixels.
- Send the PNG image over the internet.
- Send the password separately.
- Recipient uploads the PNG, enters the password, and reads your message.

**Each image has its own password.**
""")
