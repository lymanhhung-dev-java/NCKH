import streamlit as st
import requests

# Cấu hình URL của Backend FastAPI
BACKEND_URL = "http://localhost:8000/api/v1"

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Hệ thống Hỏi đáp ",
    page_icon="💬",
    layout="wide"
)

def init_session_state():
    """Khởi tạo các biến session state cần thiết"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # Biến để kiểm tra trạng thái đăng nhập của Admin
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

def render_user_interface():
    """Giao diện dành cho Người dùng: Chỉ có chức năng Chat"""
    st.title("💬 Trợ lý Hỏi đáp Tài liệu (RAG)")
    
    # Chỉ hiển thị nút xóa lịch sử chat ở sidebar khi đang ở chế độ User
    with st.sidebar:
        st.divider()
        if st.button("🗑️ Xóa lịch sử chat", type="secondary", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
            
    # Hiển thị lại lịch sử chat từ st.session_state
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Hiển thị nguồn tài liệu nếu có (dưới câu trả lời của trợ lý)
            if message["role"] == "assistant" and message.get("sources"):
                with st.expander("📚 Xem nguồn tài liệu"):
                    for idx, source in enumerate(message["sources"]):
                        filename = source.get("filename", "N/A")
                        page = source.get("page", "N/A")
                        content = source.get("content", "")
                        st.markdown(f"**Nguồn {idx + 1}:** `{filename}` (Trang {page})")
                        st.info(content)

    # Ô nhập liệu cho câu hỏi mới
    if prompt := st.chat_input("Nhập câu hỏi của bạn về tài liệu..."):
        # Thêm câu hỏi vào lịch sử và UI
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Khung hiển thị câu trả lời của AI
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Đang suy nghĩ... 🤔")
            
            try:
                # Gọi API Chat của backend
                response = requests.post(
                    f"{BACKEND_URL}/ask",
                    json={"question": prompt},
                    timeout=120  # Thời gian chờ lâu hơn vì quá trình sinh văn bản/RAG có thể chậm
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "Xin lỗi, tôi không thể tạo câu trả lời.")
                    sources = data.get("sources", [])
                    
                    # Cập nhật placeholder với câu trả lời chính thức
                    message_placeholder.markdown(answer)
                    
                    # Hiển thị các nguồn tài liệu
                    if sources:
                        with st.expander("📚 Xem nguồn tài liệu"):
                            for idx, source in enumerate(sources):
                                filename = source.get("filename", "N/A")
                                page = source.get("page", "N/A")
                                content = source.get("content", "")
                                st.markdown(f"**Nguồn {idx + 1}:** `{filename}` (Trang {page})")
                                st.info(content)
                    
                    # Lưu vào session state
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "sources": sources
                    })
                    
                else:
                    error_msg = f"❌ Lỗi từ server: HTTP {response.status_code}"
                    message_placeholder.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    
            except requests.exceptions.RequestException as e:
                error_msg = "❌ Không thể kết nối đến Backend. Vui lòng đảm bảo server đang chạy tại http://localhost:8000"
                message_placeholder.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})


def render_admin_interface():
    """Giao diện dành cho Quản trị viên: Nạp dữ liệu"""
    st.title("⚙️ Quản trị hệ thống")
    
    # Bước kiểm tra mật khẩu
    if not st.session_state.admin_authenticated:
        st.info("Khu vực này dành riêng cho quản trị viên. Vui lòng đăng nhập.")
        password = st.text_input("Nhập mật khẩu quản trị:", type="password")
        
        if password:
            # Hardcode mật khẩu theo yêu cầu (có thể thay đổi nếu cần bảo mật hơn)
            if password == "admin123":
                st.session_state.admin_authenticated = True
                st.success("Đăng nhập thành công!")
                st.rerun()  # Tải lại trang để vào giao diện admin
            else:
                st.error("Mật khẩu không chính xác.")
        
        # Ngăn chặn việc chạy các mã bên dưới nếu chưa đăng nhập
        return 
        
    # Nút đăng xuất (tùy chọn)
    with st.sidebar:
        st.divider()
        if st.button("🚪 Đăng xuất khỏi Admin", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.rerun()

    # Các tính năng của Quản trị viên (chỉ hiển thị sau khi đăng nhập thành công)
    st.subheader("📥 Nạp dữ liệu vào hệ thống RAG")
    st.markdown("Chức năng này gọi API Ingest để đọc các file tài liệu và lưu trữ vào Vector Database.")
    
    directory_path = st.text_input(
        "Đường dẫn thư mục tài liệu:", 
        value="./data",
        help="Ví dụ: ./data hoặc C:/Users/documents"
    )
    
    if st.button("🚀 Bắt đầu Nạp dữ liệu", type="primary"):
        with st.spinner("Đang gửi yêu cầu nạp dữ liệu tới Backend..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/ingest",
                    json={"directory_path": directory_path},
                    timeout=10
                )
                if response.status_code == 200:
                    st.success("✅ Nạp dữ liệu thành công! (Tiến trình đang chạy ngầm trên server)")
                else:
                    st.error(f"❌ Lỗi từ server: HTTP {response.status_code}")
            except requests.exceptions.RequestException as e:
                st.error("❌ Không thể kết nối đến Backend. Vui lòng kiểm tra lại server FastAPI!")


def main():
    # Khởi tạo state
    init_session_state()
    
    # Tạo Sidebar điều hướng
    st.sidebar.title("🧭 Menu Điều Hướng")
    
    # Sử dụng st.sidebar.radio để tạo menu 2 lựa chọn
    menu_selection = st.sidebar.radio(
        "Chọn chế độ:",
        ("💬 Dành cho Người dùng", "⚙️ Quản trị hệ thống")
    )
    
    # Định tuyến dựa trên lựa chọn
    if menu_selection == "💬 Dành cho Người dùng":
        render_user_interface()
    elif menu_selection == "⚙️ Quản trị hệ thống":
        render_admin_interface()

if __name__ == "__main__":
    main()
