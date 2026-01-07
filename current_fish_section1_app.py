import numpy as np
import streamlit as st

# --- Unit helpers ---

KNOT_TO_MS = 0.514444

def to_ms(value, unit):
    return value * KNOT_TO_MS if unit == "knots" else value

def from_ms(value_ms, unit):
    return value_ms / KNOT_TO_MS if unit == "knots" else value_ms


# --- Heading wrap helper (0–359°) ---

def wrap_deg(v):
    return int(v) % 360


# Initialize session state values

if "fish_brg" not in st.session_state:
    st.session_state.fish_brg = 0

if "ship_cse" not in st.session_state:
    st.session_state.ship_cse = 0


# --- Vector helpers ---

def polar_to_uv(speed_ms, bearing_deg):
    b = np.deg2rad(bearing_deg)
    u = speed_ms * np.sin(b)
    v = speed_ms * np.cos(b)
    return u, v

def uv_to_polar(u, v):
    speed = np.hypot(u, v)
    brg = (np.rad2deg(np.arctan2(u, v)) + 360) % 360
    return speed, brg


# --- UI ---

st.set_page_config(
    page_title="Liam Barclay – True Current",
    layout="centered"
)

st.title("Liam Barclay – True Current")
st.caption("App created by Steven Bell")
st.caption("Bearings TRUE (0° = North, clockwise).")


unit = st.radio("Select units", ["knots", "m/s"], horizontal=True)

col1, col2 = st.columns(2)


# --- FISH PANEL ---

with col1:

    st.markdown("### Fish apparent")

    fish_speed_in = st.number_input(
        f"Fish Speed ({unit})",
        value=0.0,
        step=0.1
    )

    st.write("**Fish Bearing (° TRUE)**")

    fb_minus, fb_val, fb_plus = st.columns([1,2,1])

    with fb_minus:
        if st.button("−", use_container_width=True, key="fb_dec"):
            st.session_state.fish_brg = wrap_deg(st.session_state.fish_brg - 1)

    with fb_val:
        st.markdown(
            f"<h3 style='text-align:center'>{st.session_state.fish_brg}°</h3>",
            unsafe_allow_html=True
        )

    with fb_plus:
        if st.button("+", use_container_width=True, key="fb_inc"):
            st.session_state.fish_brg = wrap_deg(st.session_state.fish_brg + 1)

    fish_brg = st.session_state.fish_brg


# --- VESSEL PANEL ---

with col2:

    st.markdown("### Vessel motion")

    ship_speed_in = st.number_input(
        f"Vessel Speed ({unit})",
        value=0.0,
        step=0.1
    )

    st.write("**Vessel Course (° TRUE)**")

    vc_minus, vc_val, vc_plus = st.columns([1,2,1])

    with vc_minus:
        if st.button("−", use_container_width=True, key="vc_dec"):
            st.session_state.ship_cse = wrap_deg(st.session_state.ship_cse - 1)

    with vc_val:
        st.markdown(
            f"<h3 style='text-align:center'>{st.session_state.ship_cse}°</h3>",
            unsafe_allow_html=True
        )

    with vc_plus:
        if st.button("+", use_container_width=True, key="vc_inc"):
            st.session_state.ship_cse = wrap_deg(st.session_state.ship_cse + 1)

    ship_cse = st.session_state.ship_cse


# --- CALCULATION ---

if st.button("Calculate TRUE current"):

    fish_speed_ms = to_ms(fish_speed_in, unit)
    ship_speed_ms = to_ms(ship_speed_in, unit)

    u_fish, v_fish = polar_to_uv(fish_speed_ms, fish_brg)
    u_ship, v_ship = polar_to_uv(ship_speed_ms, ship_cse)

    u_cur = u_fish + u_ship
    v_cur = v_fish + v_ship

    cur_speed_ms, cur_brg = uv_to_polar(u_cur, v_cur)

    cur_speed_out = from_ms(cur_speed_ms, unit)

    st.markdown("## TRUE Current Result")
    st.write(f"**Speed:** {cur_speed_out:.3f} {unit}")
    st.write(f"**Bearing:** {cur_brg:.3f} ° TRUE")

    alt_unit = "m/s" if unit == "knots" else "knots"
    st.caption(f"(= {from_ms(cur_speed_ms, alt_unit):.3f} {alt_unit})")

    with st.expander(f"Vector components (in {unit})"):
        st.write(f"Fish (E/N): {from_ms(u_fish, unit):.6f}, {from_ms(v_fish, unit):.6f}")
        st.write(f"Vessel (E/N): {from_ms(u_ship, unit):.6f}, {from_ms(v_ship, unit):.6f}")
        st.write(f"Current (E/N): {from_ms(u_cur, unit):.6f}, {from_ms(v_cur, unit):.6f}")

else:
    st.info("Enter values, then click **Calculate TRUE current**.")
