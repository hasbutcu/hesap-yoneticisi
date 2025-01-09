import tkinter as tk
import sys
from tkinter import ttk, messagebox, simpledialog
import json
import os
import uuid  # Import uuid for generating unique IDs

if getattr(sys, 'frozen', False):
    # PyInstaller tarafından paketlendiğinde
    application_path = os.path.dirname(sys.executable)
else:
    # Normal Python çalıştırmasında
    application_path = os.path.dirname(os.path.abspath(__file__))

class GameAccountManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hesap Yöneticisi")
        self.root.geometry("1200x700")  # Increased width to accommodate new column
        self.root.configure(bg='#f0f0f0')

        # AppData\Roaming\HesapYöneticisi yolunu oluştur
        self.account_manager_path = os.path.join(os.getenv('APPDATA'), 'HesapYöneticisi')
        
        # HesapYöneticisi klasörünü oluştur
        os.makedirs(self.account_manager_path, exist_ok=True)

        # Hesaplar.json dosyasının tam yolu
        self.DOSYA_ADI = os.path.join(self.account_manager_path, 'hesaplar.json')

        # Eğer JSON dosyası yoksa, boş bir dosya oluştur
        if not os.path.exists(self.DOSYA_ADI):
            with open(self.DOSYA_ADI, 'w', encoding='utf-8') as f:
                json.dump([], f)

        # Eğer JSON dosyası yoksa boş bir tane oluştur
        if not os.path.exists(self.DOSYA_ADI):
            with open(self.DOSYA_ADI, 'w', encoding='utf-8') as f:
                json.dump([], f)

        self.hesaplar = self.hesaplari_yukle()

        self.create_ui()

    def hesaplari_yukle(self):
        if os.path.exists(self.DOSYA_ADI):
            with open(self.DOSYA_ADI, "r", encoding="utf-8") as dosya:
                return json.load(dosya)
        return []

    def hesaplari_kaydet(self):
        with open(self.DOSYA_ADI, "w", encoding="utf-8") as dosya:
            json.dump(self.hesaplar, dosya, indent=4, ensure_ascii=False)

    def create_ui(self):
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Üst kontrol çubuğu
        top_frame = tk.Frame(main_frame, bg='#f0f0f0')
        top_frame.pack(side=tk.TOP, fill=tk.X, pady=10)

        # Arama çubuğu
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.dinamik_arama)
        search_entry = tk.Entry(top_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side=tk.LEFT, padx=10)
        search_label = tk.Label(top_frame, text="🔍 Hesap Ara", bg='#f0f0f0')
        search_label.pack(side=tk.LEFT)

        # Eylem butonları
        button_frame = tk.Frame(top_frame, bg='#f0f0f0')
        button_frame.pack(side=tk.RIGHT, padx=10)

        buttons = [
            ("➕ Yeni Hesap", self.hesap_ekle_dialog),
            ("✏️ Düzenle", self.hesap_duzenle_dialog),
            ("❌ Sil", self.hesap_sil_dialog)
        ]

        for text, command in buttons:
            btn = tk.Button(button_frame, text=text, command=command, 
                            bg='#4CAF50', fg='white', padx=10, pady=5)
            btn.pack(side=tk.LEFT, padx=5)

        # Hesapları görüntüleme tablosu
        self.tree = ttk.Treeview(main_frame, columns=("Oyun Hesabı", "Eposta", "Karakter", "Sunucu", "Level", "Açıklamalar"), show='headings')

        # Sütun ayarları
        column_configs = [
            
            ("Oyun Hesabı", 150),
            ("Eposta", 200),
            ("Karakter", 150),
            ("Sunucu", 150),  # New column
            ("Level", 100),
            ("Açıklamalar", 200)
        ]

        for col, width in column_configs:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=tk.CENTER)

        # Açıklama için scrollbar
        tree_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=tree_scrollbar.set)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Çift tıklama detay gösterme
        self.tree.bind('<Double-1>', self.hesap_detay_goster)

        # İlk yükleme
        self.refresh_treeview()

    def refresh_treeview(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for hesap in self.hesaplar:
            self.tree.insert('', tk.END, values=(
                hesap.get('Oyun Hesabı Adı', ''),  # Oyun Hesabı Adı ilk sütunda
                hesap.get('Eposta', ''),
                hesap.get('Karakter Adı', ''),
                hesap.get('Sunucu', ''),
                hesap.get('Level', ''),
                hesap.get('Açıklamalar', ''),
                hesap.get('ID', '')  # ID son sütunda
            ))

    def dinamik_arama(self, *args):
        """Dinamik arama fonksiyonu"""
        anahtar = self.search_var.get().lower()
        
        # Tüm öğeleri temizle
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # Filtrelenmiş hesapları ekle
        for hesap in self.hesaplar:
            # Arama kriterlerini kontrol et
            if (anahtar in hesap.get("ID", "").lower() or
                anahtar in hesap.get("Oyun Hesabı Adı", "").lower() or
                anahtar in hesap.get("Eposta", "").lower() or
                anahtar in hesap.get("Karakter Adı", "").lower() or
                anahtar in hesap.get("Sunucu", "").lower() or  # New field
                anahtar in hesap.get("Level", "").lower() or
                anahtar in hesap.get("Açıklamalar", "").lower() or
                any(anahtar in kelime.lower() for kelime in hesap.get("Anahtar Kelimeler", []))):
                
                self.tree.insert('', tk.END, values=(
                    
                    hesap.get('Oyun Hesabı Adı', ''),
                    hesap.get('Eposta', ''),
                    hesap.get('Karakter Adı', ''),
                    hesap.get('Sunucu', ''),  # New field
                    hesap.get('Level', ''),
                    hesap.get('Açıklamalar', ''),
                    hesap.get('ID', '')
                ))

    def hesap_detay_goster(self, event):
        """Hesap detaylarını ayrıntılı göster"""
        selected_item = self.tree.selection()
        if not selected_item:
            return

        # Seçilen hesabın detaylarını al
        hesap_id = self.tree.item(selected_item[0])['values'][6]
        hesap = next((h for h in self.hesaplar if h.get('ID') == hesap_id), None)

        
        if hesap:
            # Detay penceresi
            detay_pencere = tk.Toplevel(self.root)
            detay_pencere.title(f"Hesap Detayları: {hesap_id}")
            detay_pencere.geometry("500x400")

            # Detayları göster
            detay_metni = tk.Text(detay_pencere, wrap=tk.WORD, height=20, width=60)
            detay_metni.pack(padx=20, pady=20)

            # Detay metnini hazırla
            detay = f"""Oyun Hesabı Adı: {hesap.get('Oyun Hesabı Adı', '')}
Eposta: {hesap.get('Eposta', '')}
Karakter Adı: {hesap.get('Karakter Adı', '')}
Sunucu: {hesap.get('Sunucu', '')}
Level: {hesap.get('Level', '')}
Açıklamalar: {hesap.get('Açıklamalar', '')}
"""

            detay_metni.insert(tk.END, detay)
            detay_metni.config(state=tk.DISABLED)  # Düzenlenemez yap

    def hesap_ekle_dialog(self):
        """Dialog to add a new account"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Yeni Hesap Ekle")
        dialog.geometry("400x600")  # Increased height

        # Input fields
        fields = [
            "Oyun Hesabı Adı", 
            "Eposta", 
            "Karakter Adı", 
            "Sunucu",  # New field
            "Level", 
            "Açıklamalar", 
            "Anahtar Kelimeler"  # New field
        ]

        entries = {}
        for field in fields:
            label = tk.Label(dialog, text=field)
            label.pack(pady=5)
            entry = tk.Entry(dialog, width=40)
            entry.pack(pady=5)
            entries[field] = entry

        def on_submit():
            new_account = {
                "ID": str(uuid.uuid4()),  # Unique ID for the new account
                "Oyun Hesabı Adı": entries["Oyun Hesabı Adı"].get(),
                "Eposta": entries["Eposta"].get(),
                "Karakter Adı": entries["Karakter Adı"].get(),
                "Sunucu": entries["Sunucu"].get(),  # New field
                "Level": entries["Level"].get(),
                "Açıklamalar": entries["Açıklamalar"].get(),
                "Anahtar Kelimeler": entries["Anahtar Kelimeler"].get().split(",")  # Split keywords by comma
            }
            self.hesaplar.append(new_account)
            self.hesaplari_kaydet()
            self.refresh_treeview()
            dialog.destroy()

        submit_button = tk.Button(dialog, text="Ekle", command=on_submit)
        submit_button.pack(pady=20)

    def hesap_duzenle_dialog(self):
        """Dialog to edit an account"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Hata", "Lütfen düzenlemek için bir hesap seçin.")
            return

        hesap_id = self.tree.item(selected_item[0])['values'][6]
        hesap = next((h for h in self.hesaplar if h['ID'] == hesap_id), None)

        if not hesap:
            messagebox.showerror("Hata", "Hesap bulunamadı.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Hesap Düzenle")
        dialog.geometry("400x600")

        fields = [
            "Oyun Hesabı Adı", 
            "Eposta", 
            "Karakter Adı", 
            "Sunucu",  # New field
            "Level", 
            "Açıklamalar", 
            "Anahtar Kelimeler"  # New field
        ]

        entries = {}
        for field in fields:
            label = tk.Label(dialog, text=field)
            label.pack(pady=5)
            entry = tk.Entry(dialog, width=40)
            entry.insert(0, hesap.get(field, ""))  # Pre-fill the current data
            entry.pack(pady=5)
            entries[field] = entry

        def on_submit():
            hesap["Oyun Hesabı Adı"] = entries["Oyun Hesabı Adı"].get()
            hesap["Eposta"] = entries["Eposta"].get()
            hesap["Karakter Adı"] = entries["Karakter Adı"].get()
            hesap["Sunucu"] = entries["Sunucu"].get()  # New field
            hesap["Level"] = entries["Level"].get()
            hesap["Açıklamalar"] = entries["Açıklamalar"].get()
            hesap["Anahtar Kelimeler"] = entries["Anahtar Kelimeler"].get().split(",")  # Split keywords by comma
            self.hesaplari_kaydet()
            self.refresh_treeview()
            dialog.destroy()

        submit_button = tk.Button(dialog, text="Kaydet", command=on_submit)
        submit_button.pack(pady=20)

    def hesap_sil_dialog(self):
        """Dialog to delete an account"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Hata", "Lütfen silmek için bir hesap seçin.")
            return

        hesap_id = self.tree.item(selected_item[0])['values'][6]
        hesap = next((h for h in self.hesaplar if h['ID'] == hesap_id), None)

        if not hesap:
            messagebox.showerror("Hata", "Hesap bulunamadı.")
            return

        result = messagebox.askyesno("Silme Onayı", f"Hesap ({hesap.get('Oyun Hesabı Adı')}) silinsin mi?")
        if result:
            self.hesaplar = [h for h in self.hesaplar if h['ID'] != hesap_id]
            self.hesaplari_kaydet()
            self.refresh_treeview()

# Tkinter uygulamasını başlatma


root = tk.Tk()
app = GameAccountManagerApp(root)
root.mainloop()

