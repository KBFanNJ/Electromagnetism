import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 页面配置
st.set_page_config(page_title="电场与电势可视化", layout="wide")

st.title("⚡ 交互式电场与电势仿真")
st.markdown("""
通过左侧的控制面板调整电荷的数量、位置和电量。
* **背景颜色**：代表电势 ($V$)，红色为高电势，蓝色为低电势。
* **流线**：代表电场线 (E)，从正电荷指向负电荷。
""")

# --- 侧边栏配置 ---
st.sidebar.header("电荷配置")

# 控制电荷数量
num_charges = st.sidebar.slider("电荷数量", 1, 5, 2)

charges = []
for i in range(num_charges):
    with st.sidebar.expander(f"电荷 {i + 1}", expanded=True):
        col1, col2 = st.columns(2)
        # 默认设置一个偶极子配置 (如果是前两个电荷)
        default_x = -2.0 if i == 0 else (2.0 if i == 1 else 0.0)
        default_q = 1.0 if i == 0 else (-1.0 if i == 1 else 1.0)

        q = st.slider(f"电量 Q{i + 1}", -5.0, 5.0, default_q, key=f"q_{i}")
        x = col1.number_input(f"X坐标 {i + 1}", -5.0, 5.0, default_x, key=f"x_{i}")
        y = col2.number_input(f"Y坐标 {i + 1}", -5.0, 5.0, 0.0, key=f"y_{i}")
        charges.append({'q': q, 'x': x, 'y': y})


# --- 物理计算核心 ---
def calculate_field_and_potential(charges, grid_size=100, range_val=5):
    x = np.linspace(-range_val, range_val, grid_size)
    y = np.linspace(-range_val, range_val, grid_size)
    X, Y = np.meshgrid(x, y)

    Ex, Ey = np.zeros(X.shape), np.zeros(Y.shape)
    V = np.zeros(X.shape)

    k = 8.99e9  # 库仑常数 (为了演示效果，数值大小不关键，主要看相对值)

    for charge in charges:
        q = charge['q']
        xc = charge['x']
        yc = charge['y']

        # 计算距离
        dx = X - xc
        dy = Y - yc
        r2 = dx ** 2 + dy ** 2
        r = np.sqrt(r2)

        # 避免除以零 (在电荷位置加一个微小的 epsilon)
        r[r < 0.1] = 0.1
        r2[r2 < 0.01] = 0.01

        # 电场 E = k * q / r^2 (矢量叠加)
        E_mag = k * q / r2
        Ex += E_mag * (dx / r)
        Ey += E_mag * (dy / r)

        # 电势 V = k * q / r (标量叠加)
        V += k * q / r

    return X, Y, Ex, Ey, V


# --- 绘图 ---
# --- 绘图 ---
range_val = 5
X, Y, Ex, Ey, V = calculate_field_and_potential(charges, grid_size=100, range_val=range_val)

# 修改点 1: 减小 figsize (例如改成了 6x6，之前是 10x8)
fig, ax = plt.subplots(figsize=(6, 6))

# ... (这中间的绘图代码保持不变) ...
v_max = np.percentile(np.abs(V), 98)
levels = np.linspace(-v_max, v_max, 40)
cntr = ax.contourf(X, Y, V, levels=levels, cmap='coolwarm', alpha=0.8, extend='both')
plt.colorbar(cntr, ax=ax, label='电势 (V)')

strm = ax.streamplot(X, Y, Ex, Ey, color='black', linewidth=0.8, density=1.5, arrowstyle='->')

for charge in charges:
    color = 'red' if charge['q'] > 0 else 'blue'
    if charge['q'] == 0: color = 'gray'
    ax.scatter(charge['x'], charge['y'], s=200, c=color, edgecolors='white', zorder=10)
    ax.text(charge['x']+0.2, charge['y']+0.2, f"Q={charge['q']}", fontsize=10, fontweight='bold')

ax.set_aspect('equal')
ax.set_xlim(-range_val, range_val)
ax.set_ylim(-range_val, range_val)
ax.set_title(f"Electric Field Map")

# 修改点 2: 使用列 (Columns) 来居中并限制宽度
# 这是一个让布局更好看的小技巧：创建3列，把图放在中间那列
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # use_container_width=True 会填满中间这列 (col2)，因为 col2 本身不宽，所以图就变小了
    st.pyplot(fig, use_container_width=True)