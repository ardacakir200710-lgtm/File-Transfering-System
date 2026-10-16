import socket
import threading
import time
import os
import hashlib
from tkinter import Tk, Label, Entry, Button, filedialog, messagebox, StringVar, Radiobutton
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class P2PFileTransferApp:
    def __init__(self, root):
        self.root = root
        self.root.title("P2P Güvenli Dosya Aktarımı")
        self.root.geometry("400x450")

        self.mode = StringVar(value="Gonderici")
        
        Radiobutton(root, text="Gönderici (Client)", variable=self.mode, value="Gonderici", command=self.update_ui).grid(row=0, column=0, pady=10)
        Radiobutton(root, text="Alıcı (Server)", variable=self.mode, value="Alici", command=self.update_ui).grid(row=0, column=1, pady=10)

        Label(root, text="IP Adresi:").grid(row=1, column=0, sticky="w", padx=10)
        self.ip_entry = Entry(root)
        self.ip_entry.grid(row=1, column=1, pady=5)
        self.ip_entry.insert(0, "127.0.0.1")

        Label(root, text="Port:").grid(row=2, column=0, sticky="w", padx=10)
        self.port_entry = Entry(root)
        self.port_entry.grid(row=2, column=1, pady=5)
        self.port_entry.insert(0, "5000")

        Label(root, text="Şifre (E2EE için):").grid(row=3, column=0, sticky="w", padx=10)
        self.password_entry = Entry(root, show="*")
        self.password_entry.grid(row=3, column=1, pady=5)

        Label(root, text="Hız Limiti (KB/s):").grid(row=4, column=0, sticky="w", padx=10)
        self.speed_entry = Entry(root)
        self.speed_entry.grid(row=4, column=1, pady=5)
        self.speed_entry.insert(0, "1024") # Varsayılan 1 MB/s

        self.file_path = ""
        self.file_btn = Button(root, text="Dosya Seç", command=self.select_file)
        self.file_btn.grid(row=5, column=0, columnspan=2, pady=10)

        self.action_btn = Button(root, text="Gönder", command=self.start_action, bg="green", fg="white")
        self.action_btn.grid(row=6, column=0, columnspan=2, pady=20)

        self.status_label = Label(root, text="Bekleniyor...", fg="blue")
        self.status_label.grid(row=7, column=0, columnspan=2)

        self.update_ui()

    def update_ui(self):
        if self.mode.get() == "Gonderici":
            self.ip_entry.config(state="normal")
            self.file_btn.config(state="normal")
            self.speed_entry.config(state="normal")
            self.action_btn.config(text="Gönder")
        else:
            self.ip_entry.delete(0, 'end')
            self.ip_entry.insert(0, "0.0.0.0")
            self.ip_entry.config(state="disabled")
            self.file_btn.config(state="disabled")
            self.speed_entry.config(state="disabled")
            self.action_btn.config(text="Dinlemeye Başla")

    def select_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.status_label.config(text=f"Seçilen: {os.path.basename(self.file_path)}")

    def get_aes_key(self):
        # Şifreden 256-bit AES anahtarı üretir
        password = self.password_entry.get().encode()
        return hashlib.sha256(password).digest()

    def start_action(self):
        if not self.password_entry.get():
            messagebox.showerror("Hata", "Lütfen şifreleme için bir şifre belirleyin!")
            return

        port = int(self.port_entry.get())
        
        if self.mode.get() == "Gonderici":
            if not self.file_path:
                messagebox.showerror("Hata", "Lütfen bir dosya seçin!")
                return
            ip = self.ip_entry.get()
            speed = float(self.speed_entry.get()) * 1024 # Byte/s çevirimi
            threading.Thread(target=self.send_file, args=(ip, port, speed), daemon=True).start()
        else:
            threading.Thread(target=self.receive_file, args=(port,), daemon=True).start()

    def send_file(self, ip, port, speed_limit_bps):
        try:
            self.status_label.config(text="Bağlanılıyor...")
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((ip, port))

            # Şifreleme (AES-CTR) ayarları
            key = self.get_aes_key()
            nonce = os.urandom(16)
            cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
            encryptor = cipher.encryptor()

            # Önce nonce (16 byte), sonra dosya adı gönderilir
            file_name = os.path.basename(self.file_path).encode('utf-8')
            client.sendall(nonce)
            client.sendall(len(file_name).to_bytes(4, 'big'))
            client.sendall(file_name)

            # Dosyayı okuyup şifreleyerek gönderme (Hız limitli)
            self.status_label.config(text="Dosya şifreleniyor ve gönderiliyor...")
            chunk_size = 4096
            with open(self.file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    start_time = time.time()
                    
                    encrypted_chunk = encryptor.update(chunk)
                    client.sendall(encrypted_chunk)

                    # Hız Limitleme (Throttling)
                    elapsed_time = time.time() - start_time
                    expected_time = len(chunk) / speed_limit_bps
                    if elapsed_time < expected_time:
                        time.sleep(expected_time - elapsed_time)

            client.sendall(encryptor.finalize())
            self.status_label.config(text="Gönderim Tamamlandı!")
            client.close()
        except Exception as e:
            self.status_label.config(text=f"Hata: {str(e)}")

    def receive_file(self, port):
        try:
            self.status_label.config(text=f"{port} portu dinleniyor...")
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(("0.0.0.0", port))
            server.listen(1)

            conn, addr = server.accept()
            self.status_label.config(text=f"Bağlantı kuruldu: {addr}")

            key = self.get_aes_key()
            
            # Nonce ve dosya adını al
            nonce = conn.recv(16)
            name_len = int.from_bytes(conn.recv(4), 'big')
            file_name = conn.recv(name_len).decode('utf-8')

            cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
            decryptor = cipher.decryptor()

            # Şifreli veriyi al, çöz ve kaydet
            save_path = f"alinan_{file_name}"
            self.status_label.config(text="Dosya alınıyor ve çözülüyor...")
            with open(save_path, "wb") as f:
                while True:
                    encrypted_chunk = conn.recv(4096)
                    if not encrypted_chunk:
                        break
                    decrypted_chunk = decryptor.update(encrypted_chunk)
                    f.write(decrypted_chunk)
                f.write(decryptor.finalize())

            self.status_label.config(text=f"Tamamlandı! '{save_path}' kaydedildi.")
            conn.close()
            server.close()
        except Exception as e:
            self.status_label.config(text=f"Hata: {str(e)}")

if __name__ == "__main__":
    root = Tk()
    app = P2PFileTransferApp(root)
    root.mainloop()