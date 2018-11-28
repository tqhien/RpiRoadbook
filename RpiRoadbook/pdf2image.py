"""

Ce module a été adapté à partir du projet initial de Edouard Balval : pdf2image.

    pdf2image is a light wrapper for the poppler-utils tools that can convert your
    PDFs into Pillow images. It was originally written by Edouard Belval and release under a MIT license :

        MIT License

        Copyright (c) 2017 Edouard Belval

        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in all
        copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE.

    The original source code is available here : <https://github.com/Belval/pdf2image>

This program is part of RpiRoadbook

RpiRoadbook is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

RpiRoadbook is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>

Ce programme fait partie du logiciel RpiRoadbook

RpiRoadbook est un logiciel libre ; vous pouvez le redistribuer ou le modifier 
suivant les termes de la GNU General Public License telle que publiée par la 
Free Software Foundation ; soit la version 3 de la licence, soit (à votre gré) 
toute version ultérieure.

RpiRoadbook est distribué dans l'espoir qu'il sera utile, mais SANS AUCUNE GARANTIE ; 
sans même la garantie tacite de QUALITÉ MARCHANDE ou d'ADÉQUATION à UN BUT PARTICULIER. 
Consultez la GNU General Public License pour plus de détails.

Vous devez avoir reçu une copie de la GNU General Public License en même temps que ce programme ; 
si ce n'est pas le cas, consultez <http://www.gnu.org/licenses>
"""

import os
import re
import tempfile
import uuid

from io import BytesIO
from subprocess import Popen, PIPE
from PIL import Image

def convert_from_path(pdf_path, dpi=200, output_folder=None, first_page=None, last_page=None, x=None, y=None,w=None, h=None, singlefile=None, fmt='ppm', thread_count=1, userpw=None):
    """
        Description: Convert PDF to Image will throw whenever one of the condition is reached
        Parameters:
            pdf_path -> Path to the PDF that you want to convert
            dpi -> Image quality in DPI (default 200)
            output_folder -> Write the resulting images to a folder (instead of directly in memory)
            first_page -> First page to process
            last_page -> Last page to process before stopping
            fmt -> Output image format
            thread_count -> How many threads we are allowed to spawn for processing
            userpw -> PDF's password
    """

    p_count = page_count(pdf_path, userpw)

    if thread_count < 1:
        thread_count = 1

    if first_page is None:
        first_page = 1

    if last_page is None or last_page > p_count:
        last_page = p_count

    # Recalculate page count based on first and last page
    p_count = last_page - first_page + 1

    if thread_count > p_count:
        thread_count = p_count

    reminder = p_count % thread_count
    current_page = first_page
    processes = []
    for _ in range(thread_count):
        # A unique identifier for our files if the directory is not empty
        #uid = str(uuid.uuid4())
        head,tail = os.path.split(pdf_path)
        uid = os.path.splitext(tail)[0]
        # Get the number of pages the thread will be processing
        thread_page_count = p_count // thread_count + int(reminder > 0)
        # Build the command accordingly
        args, parse_buffer_func = __build_command(['pdftoppm', '-r', str(dpi), pdf_path], output_folder, current_page, current_page + thread_page_count - 1, x, y, w, h,singlefile, fmt, uid, userpw)
        # Update page values
        current_page = current_page + thread_page_count
        reminder -= int(reminder > 0)
        # Spawn the process and save its uuid
        processes.append((uid, Popen(args, stdout=PIPE, stderr=PIPE)))

    images = []
    for uid, proc in processes:
        data, _ = proc.communicate()

        if output_folder is not None:
            if singlefile is None :
                images += __load_from_output_folder(output_folder, uid)
            else: 
                images += __load_from_output_folder(output_folder, uid+'_'+singlefile)
        else:
            images += parse_buffer_func(data)

    return images

def convert_from_bytes(pdf_file, dpi=200, output_folder=None, first_page=None, last_page=None, x=None, y=None, w=None, h=None, singlefile=None, fmt='ppm', thread_count=1, userpw=None):
    """
        Description: Convert PDF to Image will throw whenever one of the condition is reached
        Parameters:
            pdf_file -> Bytes representing the PDF file
            dpi -> Image quality in DPI
            output_folder -> Write the resulting images to a folder (instead of directly in memory)
            first_page -> First page to process
            last_page -> Last page to process before stopping
            fmt -> Output image format
            thread_count -> How many threads we are allowed to spawn for processing
            userpw -> PDF's password
    """

    with tempfile.NamedTemporaryFile('wb') as f:
        f.write(pdf_file)
        f.flush()
        return convert_from_path(f.name, dpi=dpi, output_folder=output_folder, first_page=first_page, last_page=last_page, x=x, y=y, w=w, h=h,singlefile=singlefile, fmt=fmt, thread_count=thread_count, userpw=userpw)

def __build_command(args, output_folder, first_page, last_page, x, y, w, h,singlefile, fmt, uid, userpw):
    if first_page is not None:
        args.extend(['-f', str(first_page)])

    if last_page is not None:
        args.extend(['-l', str(last_page)])
        
    if x is not None:
        args.extend(['-x', str(x)])

    if y is not None:
        args.extend(['-y', str(y)])
        
    if w is not None:
        args.extend(['-W', str(w)])
        
    if h is not None:
        args.extend(['-H', str(h)])
        
    if singlefile is not None:
        args.append('-singlefile')

    parsed_format, parse_buffer_func = __parse_format(fmt)

    if parsed_format != 'ppm':
        args.append('-' + parsed_format)

    if output_folder is not None:
        if singlefile is not None :
            args.append(os.path.join(output_folder, uid+'_'+singlefile))
        else:
            args.append(os.path.join(output_folder, uid))
    if userpw is not None:
        args.extend(['-upw', userpw])
    return args, parse_buffer_func

def __parse_format(fmt):
    if fmt[0] == '.':
        fmt = fmt[1:]
    if fmt == 'jpeg' or fmt == 'jpg':
        return 'jpeg', __parse_buffer_to_jpeg
    if fmt == 'png':
        return 'png', __parse_buffer_to_png
    # Unable to parse the format so we'll use the default
    return 'ppm', __parse_buffer_to_ppm

def __parse_buffer_to_ppm(data):
    images = []

    index = 0

    while index < len(data):
        code, size, rgb = tuple(data[index:index + 40].split(b'\n')[0:3])
        size_x, size_y = tuple(size.split(b' '))
        file_size = len(code) + len(size) + len(rgb) + 3 + int(size_x) * int(size_y) * 3
        images.append(Image.open(BytesIO(data[index:index + file_size])))
        index += file_size

    return images

def __parse_buffer_to_jpeg(data):
    return [
        Image.open(BytesIO(image_data + b'\xff\xd9'))
        for image_data in data.split(b'\xff\xd9')[:-1] # Last element is obviously empty
    ]

def __parse_buffer_to_png(data):
    images = []

    index = 0

    while index < len(data):
        file_size = data[index:].index(b'IEND') + 8 # 4 bytes for IEND + 4 bytes for CRC
        images.append(Image.open(BytesIO(data[index:index+file_size])))
        index += file_size

    return images

def page_count(pdf_path, userpw=None):
    try:
        if userpw is not None:
            proc = Popen(["pdfinfo", pdf_path, '-upw', userpw], stdout=PIPE, stderr=PIPE)
        else:
            proc = Popen(["pdfinfo", pdf_path], stdout=PIPE, stderr=PIPE)

        out, err = proc.communicate()
    except:
        raise Exception('Unable to get page count. Is poppler installed and in PATH?')


    try:
        # This will throw if we are unable to get page count
        return int(re.search(r'Pages:\s+(\d+)', out.decode("utf8", "ignore")).group(1))
    except:
        raise Exception('Unable to get page count. %s' % err.decode("utf8", "ignore"))
				
def page_size(pdf_path, userpw=None):
    try:
        if userpw is not None:
            proc = Popen(["pdfinfo", pdf_path, '-upw', userpw], stdout=PIPE, stderr=PIPE)
        else:
            proc = Popen(["pdfinfo", pdf_path], stdout=PIPE, stderr=PIPE)

        out, err = proc.communicate()
    except:
        raise Exception('Unable to get page size. Is poppler installed and in PATH?')


    try:
        # This will throw if we are unable to get page count
        st = re.search(r'Page size:\s+(\d+.?\d+)\s+[x]\s+(\d+.?\d+)', out.decode("utf8", "ignore"))
        return float(st.group(1)),float(st.group(2))
    except:
        raise Exception('Unable to get page size. %s' % err.decode("utf8", "ignore"))

def __load_from_output_folder(output_folder, uid):
    return [Image.open(os.path.join(output_folder, f)) for f in sorted(os.listdir(output_folder)) if uid in f]
