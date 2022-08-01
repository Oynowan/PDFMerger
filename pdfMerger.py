from PyPDF2 import PdfReader, PdfMerger, PageRange
from PyPDF2.errors import PdfReadError
from tkinter import ttk, filedialog as fd
import tkinter as tk
import string

# FUNCTIONS

def mergingFiles():
    merger = PdfMerger()
    filesNumber = 0
    for pdf in pdfFiles:
        merging_pages = []
        if len(pdf['file']) > 0:
            try:
                file = PdfReader(pdf['file'])
            except PdfReadError:
                tk.messagebox.showerror(title="Error!", message=f"Could not read malformed PDF file '{pdf['file']}'.")
                merger.close()
                return False
            filesNumber += 1
            if ',' in pdf['pages']:
                pages = pdf['pages'].split(',')
                pages = uniqueList(pages)
                for page in pages:
                    if len(page) > 0:
                        merger.append(pdf['file'], pages=(int(page)-1, int(page), 1))
            elif '-' in pdf['pages']:

                pages = pdf['pages'].split('-')
                for index, page in enumerate(pages):
                    if len(page) < 1:
                        pages[index].pop()
                pages.sort()
                pages[0] = int(pages[0]) - 1
                if pages[1] == len(file.pages):
                    pages[1] = ''
                range_pages = f'{pages[0]}:{pages[1]}'
                merger.append(pdf['file'], pages=PageRange(range_pages))
            elif len(pdf['pages']) == 0:
                merger.append(pdf['file'])
            else:
                merging_pages.append(int(pdf['pages'])-1)
                merging_pages.append(int(pdf['pages']))
                merging_pages.append(1)
                merging_pages = tuple(merging_pages)
                merger.append(pdf['file'], pages=merging_pages)
                
    if filesNumber > 1:
        merger.write('result.pdf')
        merger.close()
    else:
        tk.messagebox.showwarning(title="Warning!", message="You can't merge no files or just one file! Please choose more files.")
        merger.close()
        return False
    
    tk.messagebox.showinfo(title="Success!", message="Your files were merged successfuly. New file result.pdf in the root.")
    return True

def uniqueList(list1):
    unique_list = []

    for x in list1:
        if x not in unique_list:
            unique_list.append(x)
    return unique_list

def validate_entry(entry_text, index, label):
    pdf = PdfReader(pdfFiles[index]['file'])

    if len(entry_text.get()) > 0:
        available_chars = list(string.digits) + [',', '-']
        digits = list(string.digits)
        text = ''.join(entry_text.get().split())

        if text[-1] not in available_chars:
            entry_text.set(text[:len(text)-1])
            return
        
        if len(text) > 1:
            if text[-1] == '-':
                if ',' in list(text) or text[-2] == '-':
                    text = text[:len(text)-1]
                
                if '-' in list(text[:-1]):
                    text = text[:len(text)-1]

            elif text[-1] == ',':
                if '-' in list(text) or text[-2] == ',':
                    text = text[:len(text)-1]
                text = text.split(',')[:-1]
                text = ','.join(uniqueList(text)) + ','
        if text[-1] in digits:
            if int(text[-1]) > len(pdf.pages):
                text = text[:-1] + str(len(pdf.pages))
            if len(text) >= 2:
                if text[-2] in digits:
                    if int(text[-2] + text[-1]) > len(pdf.pages):
                        text = text[:-2] + str(len(pdf.pages))
        if text[-1] == '0':
            if len(text) < 2:
                text = text[:-1]
            else:
                if text[-2] not in digits:
                    text = text[:-1]

        textLabel = list(text)

        if '-' not in textLabel and ',' not in textLabel:
            label['text'] = 'Pages'
        if ',' in textLabel:
            label['text'] = 'Pages'
        if '-' in textLabel:
            label['text'] = 'Range'
        try:
            if textLabel[0] == ',' or textLabel[0] == '-':
                label['text'] = "You can't begine with ',' or '-' character, only digits"
                text = ''
        except:
            pass
        pdfFiles[index]['pages'] = text
        entry_text.set(text)
    else:
        label['text'] = "All pages"
        pdfFiles[index]['pages'] = ''
        entry_text.set("")
 
def select_file_button(index):
    global number_of_buttons
    global add_button
    global pdfFilesFrame

    pdfFiles.append({'file': '', 'pages': ''})
    entry_text = tk.StringVar()

    if type(add_button) is not None:
        try:
            add_button.destroy()
            add_button = None
        except:
            pass
    buttonFrame = tk.Frame(pdfFilesFrame, padx=10, pady=10)
    buttonFrame.pack()
    numberLabel = ttk.Label(buttonFrame, text=f'{number_of_buttons + 1}.')
    numberLabel.grid(column=0, row=0, sticky=tk.W)
    open_file = ttk.Button(buttonFrame, text='Open a File', width=30, command=lambda: select_file(open_file, index, entryFile, maxPagesLabel))
    open_file.grid(column=1, row=0, sticky=tk.W)
    entryFile = ttk.Entry(buttonFrame, width=15, textvariable=entry_text)
    entryFile.config(state='disabled')
    entryFile.grid(column=2, row=0, padx=10)
    entryLabel = ttk.Label(buttonFrame, text="All pages", width=100)
    entryLabel.grid(column=3, row=0, sticky=tk.W)
    maxPagesLabel = ttk.Label(buttonFrame)
    maxPagesLabel.grid(column=1, row=1)
    entry_text.trace('w', lambda *args: validate_entry(entry_text, index, entryLabel))
    number_of_buttons += 1

def add_more_button(frame):
    global add_button

    add = ttk.Button(frame, text='+', width=window_width, command=lambda: select_file_button(number_of_buttons))
    add.pack()
    add_button = add

def select_file(button, index, entry, maxPages):
    global number_of_buttons
    global add_button

    file_types = (
        ('PDF files', '*.pdf'),
    )

    filename = fd.askopenfilename(
        title = 'Open a file',
        initialdir='/',
        filetypes=file_types
    )

    try:
        file = PdfReader(filename)
    except PdfReadError:
        tk.messagebox.showerror(title="Error!", message=f"Could not read malformed PDF file '{filename}'.")
        return False

    maxPages['text'] = f"Max pages: {len(file.pages)}"

    for index_, pdf in enumerate(pdfFiles):
        if index_ != index and filename == pdf['file'] and len(filename) != 0:
            button['text'] = 'Open a file'
            pdfFiles[index]['file'] = ''
            entry.config(state="disabled")
            tk.messagebox.showerror(title="Error!", message="You can't merge two files with the same name!")
            return 

    if len(filename) == 0:
        if number_of_buttons == 2:
            button['text'] = 'Open a file'
            pdfFiles[index]['file'] = ''
            pdfFiles[index]['pages'] = ''
            entry.config(state="disabled")
        else:
            button.master.destroy()
            number_of_buttons -= 1
            pdfFiles[index]['file'] = ''
            pdfFiles[index]['pages'] = ''
        return

    if len(filename) > 0:
        button['text'] = filename.split('/')[-1]
        pdfFiles[index]['file'] = filename
    
    number = 0
    for pdf in pdfFiles:
        if len(pdf['file']) > 0:
            number += 1

    if number_of_buttons == number and add_button == None:
        add_more_button(button.master.master)
    entry.config(state="enable")

# VARIABLES

pdfFiles = []
number_of_buttons = 0
add_button = None
window_width = 600
window_height = 800


# TKINTER SETUP

root = tk.Tk()
root.title('PDFMerger')
root.geometry(f'{window_width}x{window_height}+350+100')
root.resizable(False, True)
pdfFilesFrame = tk.Frame(root)

titleLabel = tk.Label(root, text="PDF Merger")
titleLabel.pack()
explLabel = tk.Label(root, text="Use comma(',') for specific pages, minus('-') between numbers for range or leave empty for all pages. ")
explLabel.pack()
sep = ttk.Separator(root, orient='horizontal')
sep.pack(fill='x', pady=10)
pdfFilesFrame.pack(anchor=tk.W)

select_file_button(number_of_buttons)
select_file_button(number_of_buttons)

mergeBtn = ttk.Button(root, text="Merge", command=mergingFiles, width=50)
mergeBtn.pack(padx=10, pady=10)

sep2 = ttk.Separator(root, orient='horizontal')
sep2.pack(fill='x', pady=10)

closeBtn = ttk.Button(root, text="Close", command=root.quit, width=20, padding=10)
closeBtn.pack(padx=10, pady=10)


root.mainloop()