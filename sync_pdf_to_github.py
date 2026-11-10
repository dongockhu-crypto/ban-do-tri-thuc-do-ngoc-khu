import os
import subprocess
import sys
import glob

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_cmd(cmd, desc=""):
    if desc:
        print(f"\n[+] {desc}...")
    result = subprocess.run(cmd, cwd=CURRENT_DIR, shell=True, text=True, capture_output=False)
    return result.returncode

def main():
    print("=" * 65)
    print("  HỆ THỐNG ĐỒNG BỘ TỰ ĐỘNG BẢN ĐỒ TRI THỨC VÀ FILE PDF LÊN GITHUB")
    print("=" * 65)
    
    # 1. Quét và tái tạo Bản đồ tri thức 3D và index.html
    print("\n[Bước 1/3] Quét toàn bộ kho văn bản và cập nhật Bản đồ tri thức 3D...")
    gen_script = os.path.join(CURRENT_DIR, "generate_pdf_knowledge_graph.py")
    if os.path.exists(gen_script):
        ret = run_cmd(f'"{sys.executable}" "{gen_script}"')
        if ret != 0:
            print("[!] Cảnh báo: Có lỗi khi tạo bản đồ tri thức.")
    
    # 2. Kiểm tra trạng thái thay đổi Git
    print("\n[Bước 2/3] Kiểm tra các tệp PDF mới hoặc tệp cập nhật...")
    run_cmd('git add .gitignore generate_pdf_knowledge_graph.py index.html HUONG_DAN_SU_DUNG_BAN_DO_TRI_THUC.md Mo_Ban_Do_Tri_Thuc_PDF.bat')
    run_cmd('git add "*.pdf" "*.PDF"')
    run_cmd('git add "Các văn bản đã hết hiệu lực/*.pdf"')
    
    # Kiểm tra xem có gì mới để commit không
    res = subprocess.run('git status --porcelain', cwd=CURRENT_DIR, shell=True, text=True, capture_output=True)
    if res.stdout.strip():
        print("[+] Phát hiện tệp mới / cập nhật. Đang tạo bản lưu trữ (commit)...")
        run_cmd('git commit -m "Auto sync: Cap nhat kho van ban PDF va Ban do tri thuc 3D"')
    else:
        print("[+] Các tệp hiện tại đã được ghi nhận đầy đủ.")

    # 3. Đẩy lên GitHub
    print("\n[Bước 3/3] Đang đẩy toàn bộ dữ liệu lên GitHub (dongockhu-crypto/ban-do-tri-thuc-do-ngoc-khu)...")
    print("(*) Lưu ý: Nếu là lần đầu tiên, cửa sổ trình duyệt có thể hiện lên để bạn bấm 'Authorize' xác thực tài khoản.")
    ret = run_cmd('git push -u origin main')
    
    if ret == 0:
        print("\n" + "=" * 65)
        print("  🎉 XUẤT BẢN THÀNH CÔNG 100% LÊN GITHUB PAGES!")
        print("  👉 Mọi người trong cơ quan có thể xem trực tiếp tại:")
        print("     https://dongockhu-crypto.github.io/ban-do-tri-thuc-do-ngoc-khu/")
        print("=" * 65)
    else:
        print("\n[!] Quá trình đẩy lên gặp gián đoạn. Vui lòng kiểm tra lại kết nối mạng hoặc xác thực tài khoản.")

if __name__ == "__main__":
    main()
