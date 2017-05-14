# Qt Layout Builder - User Manual

## Table of Contents
[link text](#abcd)

## Getting Started Example

    from PySide.QtGui import QApplication
    from qtlayoutbuilder.api import Builder
    
    layouts = Builder.from_multiline_string("""
        my_page             QWidget
          layout            QHBoxLayout
            left            QGroupBox(Fruits)
              layout        QVBoxLayout
                apple       QLabel(Apple)
                pear        QLabel(Pear)
                banana      QLabel(Banana)
            middle          QGroupBox(Authors)
              layout        QVBoxLayout
                dickens     QLabel(Dickens)
                adams       QLabel(Adams)
                rowling     QLabel(Rowling)
            right_btn       QPushButton(Click me!)
    """
    
    # Access the objects created like this...
    the_button = layouts.at('right_btn')
    
    app = QApplication()
    layouts.my_page.show()
    app.exec_()
    
       
This example creates a QWidget (which it refers to as *my_page*), and then sets 
that widget's layout to be a *QHBoxLayout*. Then it populates that layout with 
three items, which it refers to as *left*, *middle*, and *right_btn*. The item 
called *left* is specified as QGroupBox, and will have its title set 
to *Fruits* - by calling *setTitle()* on it. The item called *apple* 
will get the text *Apple*, by calling *setText()* on it.

The example also shows how you can access the objects created afterwards.

## Anatomy of the Input Text
Each line of input creates an object of the type specified by the second word,
and provides the builder with a name to associate with it. The indentation of 
the name words specifies the parent-child hierarchy that the builder will 
create. Children are indented in relation to their parents by two spaces.

The indented alignment of the *name* words is of central importance. But there
is no significance in the alignment of the *type words*. They are lined up in
the example solely for readability. (See later section on auto-formatting)

## Parent / Child Relationships Supported
The builder implements Qt's existing system for parent child relationships by 
automatically adding items to layouts; but goes further. As the example shows,
it can set the layout for a widget, and set the text or title on suitable 
widgets.

The full capabilities for adding children to parents are as follows:

### Creating the Standard Qt Widget/Layout Hierarchy
First the builder, uses the methods required to create the standard hierarchy
of layouts and widgets.

- addLayout(child) # Add a sub-layout to parent layout
- setLayout(child) # Set the layout for a parent widget
- addWidget(child) # Add a widget into a parent layout

For each line of input, the builder calls these methods speculatively, and 
stops at the first one that works. (Doesn't raise an exception)

If none of the above worked, the builder then tries a few more methods 
speculatively, and again stops at the first one that works. These are intended 
for some very common special cases, as follows. 
    
### Adding a QSpacerItem to a Q*BoxLayout
The builder tries calling addSpacerItem(child).
You use it like this:

    horiz       QHBoxLayout
      label1    QLabel('foo')
      spacer    QSpacerItem
      label2    QLabel('bar')
     
The builder constructs the QSpacerItem with zero horizontal and vertical sizes,
but with an *Expanding* size policy, which makes it exactly equivalent to the 
very commonly used *addStretch()* method on a Q*BoxLayout.
 
### Adding a QWidget to a QTabWidget
The builder tries calling addTab(child).
You use it like this:

    tab_widget          QTabWidget
      tab_a             QWidget
      tab_b             QWidget
      tab_c             QWidget
      
The builder names the tabs sequentially: tab_1, tab_2, ... tab_n
 
### Setting the widget for a QScrollArea
The builder tries calling setWidget(child).
You use it like this:

    scroller            QScrollArea
      content           QWidget
      
The builder also calls setWidgetResizable(True) on the QScrollArea.
(Because they work rather unintuitively otherwise).

## Omitted Special Cases
Note there are some parent child relationships that the builder cannot make
completely automatically for you, because the arguments that must be provided
to the *'add'* method cannot be guessed by the builder. An example would be
adding the children to a QGridLayout - where the builder cannot know which
rows and columns to specify.

We could have extended the input file syntax to deal with some of these
cases - but preferred to preserve the very simple, and quick to learn 
syntax.

All is not lost however - see the later section about *Incomplete 
Hierarchies* below.

<a name="abcd"></a>
## Using Objects you Instantiated Externally
The builder can incorporate objects you have instantiated somewhere else in 
your code into the layout hierarchies it makes. This is useful for objects with
more complex construction needs, and when introducing the builder incrementally
to existing code.

    my_widget      ?CustomWidget
    
This syntax will make the builder introspect your running code to find an object
of the *CustomWidget* class (or subclass), that you have **already** 
instantiated in your program and referred to with a variable called *my_widget*, 
or an attribute called *my_widget*. For example:

    my_widget = CustomWidget(), or
    something.my_widget = CustomWidget()
    
> The builder finds the object you are referring to with the help of Python's 
> garbage collector - which knows about every object that exists in your program.

Nb. It raises an error if it finds more than one object that qualifies.

## Setting the Text on Things
Anytime you put some text in parenthesis after a type word like this:

    label1      QLabel(some text)
    
The builder will try to give that text to the object created, first by trying
to call setText(), and then with setTitle().

(Good for QLabel, QPushButton, QLineEdit, QGroupBox and possibly other classes).

### Using Symbols and Icons on Buttons and Labels
The strings used by QLabels, QPushButtons etc. are Unicode. And Unicode 
includes a very wide variety of symbols and graphical icons. Like the ones
described here for example.

https://en.wikipedia.org/wiki/Miscellaneous_Symbols

See also the official reference: http://unicode.org/charts/#symbols 

These typographic symbols render very much more crisply than image-based icons, 
because of the anti-aliasing of edges implemented by the font designers. They
also remove the need to manage image resources.

You can include Unicode characters (or more properly *code-points*) in your
builder input, using the same notation as you would if you were writing a
string literal in python source code. Like this example which puts the *pencil*
symbol on a button:

    button      QPushButton(\u2709)
    
Or this example that includes the symbol for *return* or *enter* in the middle
of a label:

    label       QLabel(Press \u23ce when done.)
    
Some Unicode symbols have *code-points* above 0xFFFF, and you can encode these
again, just like in python source code. Note the upper case U and 8 instead of
4 ascii characters following. This example is a hamburger symbol. (Not the 3-bar
hamburger menu - but a **real** hamburger!)

    label       QLabel(\U0001F354)
   
Using Unicode in text in Qt is dependent on a suitably equipped font being
available, and chosen (by your Qt program) on the runtime machine.

A very convenient font that includes a wide range of symbols for Windows is 
'Lucida Sans Unicode' because it has been installed by default for all 
versions of Windows since Windows 98. To get the widest possible symbol
support try the open-source Code2000 font. 

You can specify the font from your PySide / PyQt program like this:

    widget = layouts_created.at('page')
    widget.setStyleSheet(""" * { font-family: "Lucida Sans Unicode"; } """)
    
(Or more selectively, for a widget lower in the layout hiearchy.)
   
## Taking the Input From a File

    layouts = Builder.from_file(file_path)
    
## Auto Formatting
When you use the build-from-file option, the builder will automatically 
re-format your file (in-place) to line up the right hand column, so you don't
have to waste effort on doing it (or changing it) manually. It creates a backup
each time - and adds a comment to the file about where the backups are saved.

To turn this behaviour off:

    layouts = Builder.from_file(file_path, auto_format_and_overwrite=False)
    
Auto formatting is not turned on by default for the multiline string variant of 
the API call; largely because there is nowhere obvious for the builder to 
write the reformatted version to. You can turn it on however by specifying a 
file it should write to:

    Builder.from_multiline_string(
            'the string', auto_format_and_write_to='my_file.txt')
    
## Error Handling
The builder handles all errors by raising an api.LayoutError which contains
an explanation, and the offending line number from the input.

    try:
        Builder.xxx()
    except LayoutError as e:
        print str(e)

## Comments

A comment line is a line in which the first non-space character is a hash.
The whole of that line will be ignored by the builder. 

    # I am a comment
    layouts = Builder.from_multiline_string("""
        my_page             QWidget
                            # I am a comment also
          layout            hbox
          
## Incomplete or Multiple Hierarchies

You can build multiple, (unrelated) hierarchies like this:

    page1       QWidget
      layout    QVBoxLayout
      etc...
    page2       QWidget
      layout    QVBoxLayout
      etc...
      
This can be useful when the builder cannot create the whole tree you want 
because it includes an item that the builder cannot add children to. (Like 
QGridLayout for example.) You can create seperate hierarchies for the 
children and then add them manually afterwards. E.g.

    layouts = Builder.from_multiline_string("""
        page1       QWidget
          layout    QGridLayout
          # Cannot go any further because need row/column to add children :-(
      
        # We can still make the things to go into the grid.
        cell_widget QWidget
          layout    QVBoxLayout
            label1  QLabel(foo)
            label2  QLabel(bar)
            label3  QLabel(baz)
    """
    
    # And then access the objects to finish the job.
    grid = layouts.at('layout')
    cell = layouts.at('cell_widget')
    grid.addWidget(cell, 0, 1)
    
## Limitations

These are the most common parent child relationships that the builder 
**cannot** make for you automatically:

- Cannot populate anything that has rows and columns
- Cannot populate QComboBox or QMenu
- Cannot populate the model-based widgets (like QListView)
- Doesn't deal with QMainWindow, Dockable Areas or Toolbars.
    
## Cautionary Notes
Qt itself lets you override the layout of all QWidgets, but when you are
programming layouts manually it's almost impossible to do so by accident. For
example, you wouldn't accidentally change the layout used by a QLabel in regular
code. Unfortunately you can do so accidentally rather easily with the builder's
input, like this:

    label       QLabel
      layout    QVBoxLayout
      
If you end up with layouts that have widgets bizarrely superimposed - this is the 
likely reason.
