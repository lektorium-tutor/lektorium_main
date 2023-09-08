import os
import re
import shutil
import zipfile
from bs4 import BeautifulSoup

class TildaArchive(object):
    def __init__(self, path):
        self.path = path

    def content(self, zipinfo, f):
        pass

    def extract_path(self, zipinfo):
        return False

    def done(self):
        pass

    def process(self):
        with zipfile.ZipFile(self.path) as zf:
            for zipinfo in zf.infolist():
                # парсинг контента
                with zf.open(zipinfo) as f:
                    self.content(zipinfo, f)

                # распаковка
                with zf.open(zipinfo) as f:
                    print(zipinfo.filename)
                    save_as = self.extract_path(zipinfo)
                    if save_as:
                        self.save(f, save_as)
        
        tilda_page = self.prepare_html()
        with open(self.get_full_path_tildapage(), 'w') as file:
            file.write(tilda_page)
            self.done()

    def save(self, source, targetpath):
        # Create all upper directories if necessaryd
        upperdirs = os.path.dirname(targetpath)
        if upperdirs and not os.path.exists(upperdirs):
            os.makedirs(upperdirs)
        with open(targetpath, "wb") as target:
            shutil.copyfileobj(source, target)

        return targetpath


class IrkruTildaArchive(TildaArchive):
    def __init__(self, path, material):
        super(IrkruTildaArchive, self).__init__(path)

        self.material = material
        self.styles = None
        self.scripts = None
        self.body = None

        self.extract_root = material.tilda_extract_root
        self.extract_url = material.tilda_extract_url

    def content(self, zipinfo, f):
        """
        Из html-файла парсит ссылки на стили и скрипты
        """
        filename = self.strip_project(zipinfo.filename)

        if re.match(r'page\d+.html', filename):
            html = f.read().decode('utf-8')
            self.styles, self.scripts = self.assets(html)
        elif re.match(r'files/page\d+body.html', filename):
            soup = BeautifulSoup(f.read().decode('utf-8'), 'html.parser')
            parent_tag = soup.find("div", {"class": "tilda_course_about_button"})
            general_tag = parent_tag.div
            t = soup.new_tag('include-xxx')
            general_tag.replaceWith(t)
            
            s = str(soup).replace("<include-xxx></include-xxx>", "<%include file='lektorium_main/_enroll_button.html' args='is_authenticated=is_authenticated, show_courseware_link=show_courseware_link, is_course_full=is_course_full, invitation_only=invitation_only, can_enroll=can_enroll, is_shib_course=is_shib_course, allow_anonymous=allow_anonymous, show_courseware_link=show_courseware_link, ecommerce_checkout=ecommerce_checkout, ecommerce_checkout_link=ecommerce_checkout_link' />")
            self.body = s

    def done(self):
        """
        Вызывается после обработки всех файлов
        """
        if self.styles:
            self.material.styles = '\n'.join(self.styles)

        if self.scripts:
            self.material.scripts = '\n'.join(self.scripts)

        if self.body:
            self.material.tilda_content = self.body

        self.material.save()
        
    def prepare_content(self, html):
        """Возвращает готовый к выводу хтмл"""
        # soup = BeautifulSoup(tilda_page, 'html.parser')
        # parent_tag = soup.find("div", {"class": "tilda_course_about_button"})
        
        result = html.replace('="images/', '="{}images/'.format(self.extract_url))
        result = result.replace("url('images/", "url('{}images/".format(self.extract_url))
        result = result.replace("js/jquery-1.10.2.min.js", "")
        result = result.replace('src="js/', 'src="{}js/'.format(self.extract_url))
        result = result.replace('href="css/', 'href="{}css/'.format(self.extract_url))
        result = result.replace("data-original='images/", "data-original='{}images/".format(self.extract_url))
        return result

    def prepare_html(self):
        path = self.extract_root
        for filename in os.listdir(path):
            if os.path.isfile(os.path.join(path, filename)) and 'page' in filename:
                full_path = (path + filename)
                HtmlFile = open(full_path, "r")
                return self.prepare_content(HtmlFile.read())
            
    def get_full_path_tildapage(self):
        path = self.extract_root
        for filename in os.listdir(path):
            if os.path.isfile(os.path.join(path, filename)) and 'page' in filename:
                full_path = (path + filename)
                return full_path

    def extract_path(self, zipinfo):
        filename = self.strip_project(zipinfo.filename)
        path = False

        if self.is_css(filename) or self.is_js(filename) or self.is_image(filename):
            path = os.path.join(self.extract_root, filename)
        elif self.is_another(filename):
            path = os.path.join(self.extract_root, re.sub(r'project\d+/', './', zipinfo.filename).lstrip('/'))
        return path

    @staticmethod
    def assets(html):
        styles, scripts = None, None

        link_pattern = re.compile(r'''<link[^>]+rel=["']stylesheet["'].+?>''')
        styles = link_pattern.findall(html)

        link_pattern = re.compile(r'''<script\s+src=["'].+?></script>''')
        scripts = link_pattern.findall(html)

        return styles, scripts

    @staticmethod
    def strip_project(filename):
        return re.sub(r'project\d+/', '', filename).lstrip('/')

    @staticmethod
    def is_another(filename):
        return filename.endswith('.html') or filename.endswith('.txt') or filename.endswith('.xml')

    @staticmethod
    def is_css(filename):
        return filename.startswith('css/') and filename.endswith('.css')

    @staticmethod
    def is_js(filename):
        return filename.startswith('js/') and filename.endswith('.js') and not filename.startswith('js/jquery-1.10.2.min.js')

    @staticmethod
    def is_image(filename):
        return re.match(r'(project\d+/)?images/[-a-z0-9_]+\.(png|jpg|jpeg|svg)', filename, re.I)