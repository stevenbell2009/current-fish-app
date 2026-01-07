import numpy as np
import streamlit as st

# --- Unit helpers ---

KNOT_TO_MS = 0.514444  # 1 knot = 0.514444 m/s

def to_ms(value, unit):
    return value * KNOT_TO_MS if unit == "knots" else value

def from_ms(value_ms, unit):
    return value_ms / KNOT_TO_MS if unit == "knots" else value_ms


# --- Heading wrap helper (0–359°) ---

def wrap_deg(value: int) -> int:
    """Wrap any integer heading into 0–359°."""
    return int(value) % 360


# --- Vector helpers (always operate in m/s) ---

def polar_to_uv(speed_ms, bearing_deg):
    """
    0° = North, clockwise.
    Returns (u_east, v_north) in m/s.
    """
    b_rad = np.deg2rad(bearing_deg)
    u = speed_ms * np.sin(b_rad)  # east
    v = speed_ms * np.cos(b_rad)  # north
    return u, v

def uv_to_polar(u, v):
    """
    Returns (speed_ms, bearing_deg) with 0° = North, clockwise.
    """
    speed = np.hypot(u, v)
    brg_rad = np.arctan2(u, v)
    brg_deg = (np.rad2deg(brg_rad) + 360.0) % 360.0
    return speed, brg_deg


# --- UI ---

st.set_page_config(
    page_title="Liam Barclay – True Current",
    layout="centered"
)

st.title("Liam Barclay – True Current")
st.caption("App created by Steven Bell")
st.caption("Bearings TRUE (0° = North, clockwise). Speeds in selected units.")

unit = st.radio("Select units", ["knots", "m/s"], horizontal=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Fish apparent")

    fish_speed_in = st.number_input(
        f"Fish Speed ({unit})",
        value=0.0,
        step=0.1
    )

    fish_brg_raw = st.number_input(
        "Fish Bearing (° TRUE)",
        value=0,
        step=1,
        format="%d",
        key="fish_brg"
    )

    # Wrap to 0–359° and write back so the display never shows 500, -10, etc.
    fish_brg = wrap_deg(fish_brg_raw)
    if fish_brg != fish_brg_raw:
        st.session_state["fish_brg"] = fish_brg


with col2:
    st.markdown("### Vessel motion")

    ship_speed_in = st.number_input(
        f"Vessel Speed ({unit})",
        value=0.0,
        step=0.1
    )

    ship_cse_raw = st.number_input(
        "Vessel Course (° TRUE)",
        value=0,
        step=1,
        format="%d",
        key="ship_cse"
    )

    # Wrap to 0–359° and write back
    ship_cse = wrap_deg(ship_cse_raw)
    if ship_cse != ship_cse_raw:
        st.session_state["ship_cse"] = ship_cse


if st.button("Calculate TRUE current"):

    # Convert speeds -> m/s
    fish_speed_ms = to_ms(fish_speed_in, unit)
    ship_speed_ms = to_ms(ship_speed_in, unit)

    # Compute vectors
    u_fish, v_fish = polar_to_uv(fish_speed_ms, fish_brg)
    u_ship, v_ship = polar_to_uv(ship_speed_ms, ship_cse)

    # TRUE current = Fish + Vessel
    u_cur = u_fish + u_ship
    v_cur = v_fish + v_ship
    cur_speed_ms, cur_brg = uv_to_polar(u_cur, v_cur)

    # Convert output to selected unit
    cur_speed_out = from_ms(cur_speed_ms, unit)

    st.markdown("## TRUE Current Result")
    st.write(f"**Speed:** {cur_speed_out:.3f} {unit}")
    st.write(f"**Bearing:** {cur_brg:.3f} ° TRUE")

    # Show alternate unit also
    alt_unit = "m/s" if unit == "knots" else "knots"
    cur_speed_alt = from_ms(cur_speed_ms, alt_unit)
    st.caption(f"(= {cur_speed_alt:.3f} {alt_unit})")

    with st.expander(f"Vector components (in {unit})"):
        u_fish_out = from_ms(u_fish, unit)
        v_fish_out = from_ms(v_fish, unit)
        u_ship_out = from_ms(u_ship, unit)
        v_ship_out = from_ms(v_ship, unit)
        u_cur_out = from_ms(u_cur, unit)
        v_cur_out = from_ms(v_cur, unit)

        st.write(f"Fish East / North: ({u_fish_out:.6f}, {v_fish_out:.6f})")
        st.write(f"Vessel East / North: ({u_ship_out:.6f}, {v_ship_out:.6f})")
        st.write(f"Current East / North: ({u_cur_out:.6f}, {v_cur_out:.6f})")

else:
    st.info("Enter values, then click **Calculate TRUE current**.")
