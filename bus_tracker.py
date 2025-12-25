import streamlit as st
import pandas as pd
import numpy as np
import cv2
from PIL import Image
import time

# --- REASONING AGENT LAYER ---
class BusTruthAgent:
    """
    The 'Truth-Seeker' Agent: Synthesizes hardware, driver, and passenger 
    telemetry to determine the bus's actual location probability.
    """
    def evaluate_location(self, hw_gps, driver_face_active, driver_mobile, mesh_passengers):
        # 1. Start with high suspicion if hardware is offline
        if hw_gps == "OFFLINE":
            # 2. Check Driver 'Prime Evidence'
            if driver_face_active and driver_mobile == "ON_ROUTE":
                # 3. Cross-validate with Passenger Mesh
                if mesh_passengers >= 3:
                    return 98, "VERIFIED BY RIDER MESH", "SUCCESS: High-confidence location via passenger & driver mesh."
                elif mesh_passengers > 0:
                    return 75, "PROBABLE LOCATION", "CAUTION: Hardware down. Location estimated via driver and few riders."
                else:
                    return 45, "STATUS UNCERTAIN", "WARNING: Hardware down. Only driver mobile detected."
            else:
                return 5, "GHOST BUS ALERT", "ERROR: No reliable signal from bus, driver, or mesh. Likely out of service."
        
        # Hardware is active
        return 100, "HARDWARE LIVE", "Bus is actively broadcasting GPS signal."

# --- DRIVER-SIDE FACE DETECTION (Simplified for local use) ---
def detect_driver_presence(image):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    img_array = np.array(image.convert('RGB'))
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    return len(faces) > 0

# --- UI CONFIGURATION ---
st.set_page_config(page_title="TransitMesh Truth-Seeker", layout="wide")
st.title("🚌 TransitMesh: End-to-End Agentic Bus Tracking")
st.markdown("---")

# --- SIDEBAR: SENSOR INPUTS (Simulating Real-Time Feeds) ---
st.sidebar.header("📡 Live Sensor Inputs")
hw_status = st.sidebar.selectbox("Bus Onboard GPS", ["LIVE", "OFFLINE"])
driver_mob = st.sidebar.selectbox("Driver Mobile GPS", ["ON_ROUTE", "UNKNOWN"])
passenger_mesh = st.sidebar.slider("Opted-in Passengers on Bus", 0, 20, 5)

st.sidebar.subheader("📸 Driver Cabin Feed")
driver_img = st.sidebar.camera_input("Verify Driver Presence")

# --- MAIN DASHBOARD ---
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🗺️ Real-Time Map & Verification")
    # Simulation Logic
    agent = BusTruthAgent()
    
    # Check if driver face is detected in the feed
    face_active = False
    if driver_img:
        img = Image.open(driver_img)
        face_active = detect_driver_presence(img)
        if face_active:
            st.success("✅ Driver Identity Verified (Face Detection Active)")
        else:
            st.warning("⚠️ Driver Not Detected in Frame")

    # Run the Agent Reasoning
    conf, status, msg = agent.evaluate_location(hw_status, face_active, driver_mob, passenger_mesh)
    
    # UI Output based on Agent Decision
    st.metric(label="Agent Confidence Score", value=f"{conf}%", delta=f"{conf-50}% if hardware fails")
    
    if conf > 80:
        st.success(f"**{status}**: {msg}")
    elif conf > 40:
        st.warning(f"**{status}**: {msg}")
    else:
        st.error(f"**{status}**: {msg}")

    # Mock Map Representation
    st.map(pd.DataFrame({'lat': [40.4406], 'lon': [-79.9959]})) # Center: CMU/Pittsburgh area

with col2:
    st.header("📊 Multi-Modal Integrity")
    st.write("**Data Source Health:**")
    st.json({
        "Hardware_GPS": "Healthy" if hw_status == "LIVE" else "FAILED",
        "Driver_Mobile": "Active" if driver_mob == "ON_ROUTE" else "Stale",
        "Passenger_Mesh": f"{passenger_mesh} Devices Active",
        "Driver_Vision": "Verified" if face_active else "Incomplete"
    })
    
    if st.button("Manual Vibe Check (User)"):
        with st.spinner("Pinging active passenger devices..."):
            time.sleep(1)
            st.info(f"Mesh Check: {passenger_mesh} devices confirmed at 40.4406, -79.9959.")

st.markdown("---")
st.caption("Product Note: This prototype demonstrates the Reasoning Agent's ability to maintain tracking when primary hardware fails.")