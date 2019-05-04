from IPython.core.magic_arguments import (argument, magic_arguments, parse_argstring)

from IPython.core.magic import (register_line_magic, register_cell_magic,
                                register_line_cell_magic)

from IPython.display import display_javascript

import requests
import json
import os




@register_line_magic
@magic_arguments()
@argument('-f', '--file', help='name or number of the source notebook', default=None)
@argument('n', type=int, help='cell number', default = None, nargs='?') 
def C(arg):
    '''
    Copy a cell from a source notebook.
    '''
    
    # parse arguments
    args = parse_argstring(C, arg)
    n = args.n
    fname = args.file
    
    # numbered notebooks
    numbered_notebooks = ["CDSE_Python_Test.ipynb",
                          "CDSE_Python1.ipynb",
                          "CDSE_Python2.ipynb",
                          "CDSE_Python3.ipynb",
                          "CDSE_Python4.ipynb",
                          ]
    
    #medadata file for storing source notebook name and cells number
    metadata_f = "copy_cell_metadata.json"
    
    # default - use if no notebook has been specified
    default_notebook = numbered_notebooks[0]
    
    
    # get notebook file name and cell number from metadata or initialize defaults
    try:
        with open(metadata_f, 'r') as f:
            meta = json.load(f)
    except FileNotFoundError:
        meta = {'n': 0, 'fname' : default_notebook}
        with open(metadata_f, 'w') as f:
            json.dump(meta, f)
         
    meta_n = meta['n']
    meta_fname = meta['fname']
      
    # check if numbered notebook, if so get the file name 
    if fname != None:
        try:
            # check if numbered notebook
            nb_num = int(fname) 
            if nb_num in range(len(numbered_notebooks)):
                fname = numbered_notebooks[nb_num]
            else:
                print(f"Error: No such notebook. Available notebooks 0-{len(numbered_notebooks)-1}.")
                return
        except ValueError:
            pass    
    # if notebook file name not specified use the file name from metadata
    else:
        fname = meta_fname

    # read the notebook file
    try:
        with open(fname) as foo:
            nb = foo.read()
    except FileNotFoundError:
        print(f"Error: File {fname} not found.")
        return
        
    # if file name is changed and no cell number is specified reset the cell counter
    if n == None:
        if meta_fname != fname:
            n = 0
        else:
            n = meta_n 
    
    #save updated metadata
    meta['n'] = n+1
    meta['fname'] = fname 
    with open(metadata_f, 'w') as f:
            json.dump(meta, f)
    

    # get content of the copied cell
    try:
        cell = json.loads(nb)['cells'][n]
    except IndexError:
        print(f"Error: No cell of index {n}. Cell range: 0-{len(json.loads(nb)['cells'])-1}.")
        return
    src_txt = ''.join(cell['source']).replace("`", "\`").replace("\\", "\\\\" )
    
    # prepare string to be copied; add cell label for reference
    if cell['cell_type'] == "markdown":
        idx = '\n\n<code style="font-size:12px;">Cell ' +str(n) + '</code>'
        txt = src_txt + idx
    else:
        idx = '#Cell '+ str(n) + '\n'
        # for code cells with magics:
        if src_txt[0] == '%':
              line_list = src_txt.split('\n')
              line_list.insert(1, idx.strip())
              txt = '\n'.join(line_list)   
        else:
              txt = idx + src_txt
    
    # render cell if markdown
    if cell['cell_type'] == "markdown":
        tm = "Jupyter.notebook.to_markdown(t_index);\n"
    else:
        tm = ""
    
    # string with JavaScript
    s = f"""var t_cell = Jupyter.notebook.insert_cell_above();
    t_cell.set_text(`{txt}`);
    var output_area = this;
    var t_index = Jupyter.notebook.get_cells().indexOf(t_cell);
    {tm}
    Jupyter.notebook.get_cell(t_index).render();
    var cell_element = output_area.element.parents('.cell');
    var cell_idx = Jupyter.notebook.get_cell_elements().index(cell_element);
    var cell = Jupyter.notebook.get_cell(cell_idx);
    Jupyter.notebook.delete_cell(cell_idx);
    Jupyter.notebook.save_checkpoint();
    """
    
    # execute Javascript
    display_javascript(s, raw=True)