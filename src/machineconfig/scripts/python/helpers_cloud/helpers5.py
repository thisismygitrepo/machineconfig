def get_jupyter_notebook(python_code: str):
    template = """
{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "7412902a-3074-475b-9820-71b82e670a2a",
   "metadata": {},
   "outputs": [],
   "source": [
    "\n",
    "import math"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
"""
    template.replace('"import math"', python_code)
    return template


# def create_jupyter_notebook(py_script: str) -> None:
#     import nbformat as nbf
#     from nbformat.notebooknode import NotebookNode
#     nb: NotebookNode = nbf.v4.new_notebook()
#     nb.cells.append(nbf.v4.new_code_cell(py_script))
#     with open("new_notebook.ipynb", mode="w", encoding="utf-8") as f:
#         nbf.write(nb,f)
