import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import ssl
import socket
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from datetime import datetime
import time
import threading
import webbrowser

class WebsiteCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Adem Website Analyzer © 2025")
        self.root.geometry("1000x800")
        self.root.configure(bg='#121212')  # خلفية سوداء
        self.running = False
        
        # ألوان التصميم المحدثة (تتناسب مع الخلفية السوداء)
        self.colors = {
            'primary': '#3498db',
            'secondary': '#121212',
            'success': '#2ecc71',
            'danger': '#e74c3c',
            'warning': '#f39c12',
            'info': '#1abc9c',
            'dark': '#1e1e1e',
            'light': '#ffffff',
            'background': '#121212',
            'text': '#ffffff'
        }
        
        self.setup_ui()
        self.setup_menu()
    
    def setup_ui(self):
        """تهيئة واجهة المستخدم الرئيسية"""
        # Header Frame
        header_frame = tk.Frame(self.root, bg=self.colors['dark'])
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        tk.Label(header_frame,
                text="أداة Adem لفحص المواقع",
                font=('Arial', 24, 'bold'),
                fg=self.colors['primary'],
                bg=self.colors['dark']).pack(pady=10)
        
        # Input Frame
        input_frame = tk.Frame(self.root, bg=self.colors['background'])
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(input_frame,
                text="رابط الموقع:",
                font=('Arial', 12),
                fg=self.colors['light'],
                bg=self.colors['background']).pack(side=tk.LEFT)
        
        self.url_entry = ttk.Entry(input_frame, width=60, font=('Arial', 12))
        self.url_entry.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        self.url_entry.insert(0, "https://example.com")
        
        # Buttons Frame
        buttons_frame = tk.Frame(self.root, bg=self.colors['background'])
        buttons_frame.pack(fill=tk.X, padx=20, pady=10)
        
        button_style = {
            'font': ('Arial', 11, 'bold'),
            'width': 15,
            'bd': 0,
            'relief': tk.RAISED,
            'padx': 10,
            'pady': 8
        }
        
        self.performance_btn = tk.Button(buttons_frame,
                                      text="فحص الأداء",
                                      command=lambda: self.start_check('performance'),
                                      bg=self.colors['primary'],
                                      fg='white',
                                      **button_style)
        self.performance_btn.pack(side=tk.LEFT, padx=5, expand=True)
        
        self.ssl_btn = tk.Button(buttons_frame,
                               text="فحص SSL",
                               command=lambda: self.start_check('ssl'),
                               bg=self.colors['info'],
                               fg='white',
                               **button_style)
        self.ssl_btn.pack(side=tk.LEFT, padx=5, expand=True)
        
        self.links_btn = tk.Button(buttons_frame,
                                 text="فحص الروابط",
                                 command=lambda: self.start_check('links'),
                                 bg=self.colors['warning'],
                                 fg='white',
                                 **button_style)
        self.links_btn.pack(side=tk.LEFT, padx=5, expand=True)
        
        self.full_btn = tk.Button(buttons_frame,
                                text="فحص شامل",
                                command=lambda: self.start_check('full'),
                                bg=self.colors['success'],
                                fg='white',
                                **button_style)
        self.full_btn.pack(side=tk.LEFT, padx=5, expand=True)
        
        self.stop_btn = tk.Button(buttons_frame,
                                text="إيقاف",
                                command=self.stop_check,
                                bg=self.colors['danger'],
                                fg='white',
                                state=tk.DISABLED,
                                **button_style)
        self.stop_btn.pack(side=tk.LEFT, padx=5, expand=True)
        
        # Progress Frame
        self.progress_frame = tk.Frame(self.root, bg=self.colors['background'])
        self.progress_frame.pack(fill=tk.X, padx=20, pady=(10, 5))
        
        tk.Label(self.progress_frame,
                text="حالة الفحص:",
                font=('Arial', 10),
                fg=self.colors['light'],
                bg=self.colors['background']).pack(side=tk.LEFT)
        
        style = ttk.Style()
        style.configure('Custom.Horizontal.TProgressbar',
                      background=self.colors['primary'],
                      troughcolor=self.colors['dark'],
                      bordercolor=self.colors['dark'])
        
        self.progress = ttk.Progressbar(self.progress_frame,
                                      orient=tk.HORIZONTAL,
                                      mode='determinate',
                                      style='Custom.Horizontal.TProgressbar')
        self.progress.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(10, 0))
        
        self.status_label = tk.Label(self.progress_frame,
                                   text="جاهز",
                                   font=('Arial', 10),
                                   fg=self.colors['light'],
                                   bg=self.colors['background'])
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Results Frame
        results_frame = tk.Frame(self.root, bg=self.colors['background'])
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        tk.Label(results_frame,
                text="نتائج الفحص:",
                font=('Arial', 12, 'bold'),
                fg=self.colors['primary'],
                bg=self.colors['background']).pack(anchor=tk.W, pady=(0, 5))
        
        self.result_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            font=('Arial', 10),
            bg=self.colors['dark'],
            fg=self.colors['light'],
            insertbackground='white',
            selectbackground=self.colors['primary'],
            padx=10,
            pady=10
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        self.setup_text_tags()
        self.setup_hover_effects()
    
    def setup_menu(self):
        """تهيئة قائمة التطبيق"""
        menubar = tk.Menu(self.root, bg=self.colors['dark'], fg=self.colors['light'])
        
        # قائمة ملف
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['dark'], fg=self.colors['light'])
        file_menu.add_command(label="خروج", command=self.root.quit)
        menubar.add_cascade(label="ملف", menu=file_menu)
        
        # قائمة مساعدة
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['dark'], fg=self.colors['light'])
        help_menu.add_command(label="عن الأداة", command=self.show_about)
        menubar.add_cascade(label="مساعدة", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def setup_text_tags(self):
        """تهيئة أنماط النص"""
        self.result_text.tag_config('header', font=('Arial', 12, 'bold'), foreground=self.colors['primary'])
        self.result_text.tag_config('success', foreground=self.colors['success'])
        self.result_text.tag_config('error', foreground=self.colors['danger'])
        self.result_text.tag_config('warning', foreground=self.colors['warning'])
        self.result_text.tag_config('info', foreground=self.colors['info'])
        self.result_text.tag_config('link', foreground=self.colors['primary'], underline=1)
        
        self.result_text.tag_bind('link', '<Button-1>', self.open_link)
    
    def setup_hover_effects(self):
        """إعداد تأثيرات مرور الماوس"""
        buttons = {
            self.performance_btn: self.colors['primary'],
            self.ssl_btn: self.colors['info'],
            self.links_btn: self.colors['warning'],
            self.full_btn: self.colors['success'],
            self.stop_btn: self.colors['danger']
        }
        
        for btn, color in buttons.items():
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(bg=self.lighten_color(c)))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))
    
    def lighten_color(self, hex_color, factor=0.2):
        """تفتيح اللون بنسبة معينة"""
        try:
            hex_color = hex_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            lighter = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
            return f'#{lighter[0]:02x}{lighter[1]:02x}{lighter[2]:02x}'
        except:
            return self.colors['primary']
    
    def start_check(self, check_type):
        """بدء عملية الفحص"""
        if self.running:
            messagebox.showwarning("تنبيه", "يوجد فحص قيد التنفيذ بالفعل!")
            return
            
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("خطأ", "الرجاء إدخال رابط الموقع")
            return
        
        if not self.is_valid_url(url):
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            if not self.is_valid_url(url):
                messagebox.showerror("خطأ", "رابط الموقع غير صالح")
                return
        
        self.running = True
        self.toggle_buttons_state(False)
        self.stop_btn.config(state=tk.NORMAL)
        self.clear_results()
        
        threading.Thread(
            target=self.run_check,
            args=(url, check_type),
            daemon=True
        ).start()
    
    def run_check(self, url, check_type):
        """تنفيذ عملية الفحص"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            checks = {
                'performance': lambda: self.check_performance(url),
                'ssl': lambda: self.check_ssl(domain),
                'links': lambda: self.check_broken_links(url),
                'full': lambda: self.full_check(url, domain)
            }
            
            if check_type in checks:
                checks[check_type]()
            
            if self.running:
                self.append_result("\nتم الانتهاء من الفحص بنجاح\n", 'success')
                self.update_status("اكتمل")
        except Exception as e:
            self.append_result(f"\nحدث خطأ غير متوقع: {str(e)}\n", 'error')
            self.update_status("فشل")
        finally:
            self.running = False
            self.toggle_buttons_state(True)
            self.stop_btn.config(state=tk.DISABLED)
    
    def full_check(self, url, domain):
        """تنفيذ فحص شامل"""
        steps = [
            (20, lambda: self.check_performance(url)),
            (40, lambda: self.check_ssl(domain)),
            (80, lambda: self.check_broken_links(url)),
            (100, lambda: None)
        ]
        
        for progress, func in steps:
            if not self.running:
                break
            func()
            self.update_progress(progress)
    
    def check_performance(self, url):
        """فحص أداء الموقع"""
        self.append_result("\n[فحص أداء الموقع]\n", 'header')
        self.update_status("جاري فحص الأداء...")
        
        response_times = []
        status_codes = []
        
        for i in range(3):
            if not self.running:
                return
                
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10)
                end_time = time.time()
                
                response_time = end_time - start_time
                response_times.append(response_time)
                status_codes.append(response.status_code)
                
                msg = f"المحاولة {i+1}: {response_time:.2f} ثانية - الحالة: {response.status_code}"
                self.append_result(msg + "\n", 'info')
            except requests.exceptions.RequestException as e:
                msg = f"المحاولة {i+1}: فشل - {str(e)}"
                self.append_result(msg + "\n", 'error')
        
        if response_times and self.running:
            avg_time = sum(response_times) / len(response_times)
            self.append_result(f"\nمتوسط زمن الاستجابة: {avg_time:.2f} ثانية\n", 'info')
            
            if avg_time < 1:
                rating = "ممتاز"
                tag = 'success'
            elif avg_time < 3:
                rating = "جيد"
                tag = 'info'
            elif avg_time < 5:
                rating = "متوسط"
                tag = 'warning'
            else:
                rating = "ضعيف"
                tag = 'error'
            
            self.append_result(f"التقييم: {rating}\n", tag)
    
    def check_ssl(self, domain):
        """فحص شهادة SSL"""
        self.append_result("\n[فحص شهادة SSL]\n", 'header')
        self.update_status("جاري فحص شهادة SSL...")
        
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
            
            expires = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            days_left = (expires - datetime.now()).days
            
            issuer = next((item[0][1] for item in cert['issuer'] if item[0][0] == 'organizationName'), "غير معروف")
            
            self.append_result(f"المصدر: {issuer}\n", 'info')
            self.append_result(f"تنتهي الصلاحية: {expires.strftime('%Y-%m-%d')}\n", 'info')
            self.append_result(f"الأيام المتبقية: {days_left}\n", 'info')
            
            if days_left < 0:
                status = "منتهية الصلاحية!"
                tag = 'error'
            elif days_left < 7:
                status = "تنتهي خلال أسبوع!"
                tag = 'error'
            elif days_left < 30:
                status = "تنتهي قريباً"
                tag = 'warning'
            else:
                status = "سارية المفعول"
                tag = 'success'
            
            self.append_result(f"الحالة: {status}\n", tag)
            
        except socket.timeout:
            self.append_result("انتهت المهلة أثناء محاولة الاتصال\n", 'error')
        except Exception as e:
            self.append_result(f"فشل في فحص SSL: {str(e)}\n", 'error')
    
    def check_broken_links(self, url):
        """فحص الروابط المعطوبة"""
        self.append_result("\n[فحص الروابط]\n", 'header')
        self.update_status("جاري فحص الروابط...")
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                self.append_result(f"لا يمكن فحص الروابط، حالة الصفحة: {response.status_code}\n", 'error')
                return
            
            soup = BeautifulSoup(response.text, 'html.parser')
            links = set()
            
            for tag in soup.find_all(['a', 'img', 'link', 'script']):
                if not self.running:
                    return
                    
                attr = 'href' if tag.name == 'a' else 'src' if tag.name in ['img', 'script'] else 'href'
                link = tag.get(attr, '')
                
                if link and not link.startswith(('mailto:', 'tel:', 'javascript:', '#')):
                    if not link.startswith('http'):
                        link = requests.compat.urljoin(url, link)
                    links.add(link)
            
            total_links = len(links)
            if total_links == 0:
                self.append_result("لم يتم العثور على روابط للفحص\n", 'warning')
                return
                
            self.append_result(f"تم العثور على {total_links} روابط\n", 'info')
            self.append_result("جاري الفحص...\n", 'info')
            
            working_links = []
            broken_links = []
            
            for i, link in enumerate(links, 1):
                if not self.running:
                    return
                    
                progress = 10 + (i / total_links) * 90
                self.update_progress(progress)
                self.update_status(f"جاري فحص الروابط ({i}/{total_links})")
                
                try:
                    response = requests.head(link, allow_redirects=True, timeout=5)
                    if response.status_code >= 400:
                        broken_links.append((link, response.status_code))
                        self.append_result(f"[{i}] معطوب: {link} (الحالة: {response.status_code})\n", 'error')
                    else:
                        working_links.append((link, response.status_code))
                        self.append_result(f"[{i}] صالح: {link}\n", 'success')
                except Exception as e:
                    broken_links.append((link, str(e)))
                    self.append_result(f"[{i}] خطأ: {link} - {str(e)}\n", 'error')
            
            self.append_result("\nملخص النتائج:\n", 'header')
            self.append_result(f"الروابط الصالحة: {len(working_links)}\n", 'success')
            self.append_result(f"الروابط المعطوبة: {len(broken_links)}\n", 'error' if broken_links else 'success')
            
            if broken_links:
                self.append_result("\nتفاصيل الروابط المعطوبة:\n", 'header')
                for link, error in broken_links[:10]:
                    self.append_result(f"• {link} => {error}\n", 'error')
                
                if len(broken_links) > 10:
                    self.append_result(f"و {len(broken_links)-10} روابط معطوبة أخرى\n", 'info')
        
        except Exception as e:
            self.append_result(f"حدث خطأ أثناء فحص الروابط: {str(e)}\n", 'error')
    
    def stop_check(self):
        """إيقاف الفحص الجاري"""
        self.running = False
        self.append_result("\nتم إيقاف الفحص بواسطة المستخدم\n", 'warning')
        self.update_status("تم الإيقاف")
    
    def is_valid_url(self, url):
        """التحقق من صحة الرابط"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False
    
    def toggle_buttons_state(self, state):
        """تفعيل/تعطيل أزرار الواجهة"""
        buttons = [self.performance_btn, self.ssl_btn, self.links_btn, self.full_btn]
        for btn in buttons:
            btn.config(state=tk.NORMAL if state else tk.DISABLED)
    
    def clear_results(self):
        """مسح نتائج الفحص السابقة"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.progress['value'] = 0
    
    def append_result(self, text, tag=None):
        """إضافة نص إلى منطقة النتائج"""
        self.root.after(0, lambda: self._append_result(text, tag))
    
    def _append_result(self, text, tag):
        """الدالة المساعدة لإضافة النتائج"""
        self.result_text.config(state=tk.NORMAL)
        if tag:
            self.result_text.insert(tk.END, text, tag)
        else:
            self.result_text.insert(tk.END, text)
        self.result_text.config(state=tk.DISABLED)
        self.result_text.see(tk.END)
    
    def update_progress(self, value):
        """تحديث شريط التقدم"""
        self.root.after(0, lambda: self.progress.configure(value=value))
    
    def update_status(self, text):
        """تحديث نص حالة الفحص"""
        self.root.after(0, lambda: self.status_label.config(text=text))
    
    def show_about(self):
        """عرض نافذة حول التطبيق"""
        about_text = """
أداة Adem لفحص المواقع
الإصدار: 2.0
المطور: Adem
سنة التطوير: 2025

مميزات الأداة:
- فحص أداء الموقع
- فحص شهادات SSL
- كشف الروابط المعطوبة
- واجهة مستخدم سهلة

جميع الحقوق محفوظة © 2025
"""
        messagebox.showinfo("عن الأداة", about_text.strip())
    
    def open_link(self, event):
        """فتح الروابط عند النقر عليها"""
        widget = event.widget
        index = widget.index(f"@{event.x},{event.y}")
        tag_names = widget.tag_names(index)
        
        if "link" in tag_names:
            url = widget.get(f"{index} wordstart", f"{index} wordend")
            try:
                webbrowser.open(url)
            except:
                messagebox.showerror("خطأ", f"تعذر فتح الرابط: {url}")

if __name__ == "__main__":
    root = tk.Tk()
    
    # إعداد النمط العام
    style = ttk.Style()
    style.theme_use('clam')
    
    # تخصيص مظهر التطبيق
    try:
        root.iconbitmap(default='siteicon.ico')  # يمكنك إضافة أيقونة إذا كنت تملك ملف icon.ico
    except:
        pass
    
    app = WebsiteCheckerApp(root)
    
    # تذييل حقوق النشر
    footer = tk.Frame(root, bg='#121212')
    footer.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
    
    tk.Label(footer,
            text="Adem Website Analyzer © 2025 - جميع الحقوق محفوظة",
            font=('Arial', 8),
            fg='#ffffff',
            bg='#121212').pack(pady=5)
    
    root.mainloop()
