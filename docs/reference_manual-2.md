# User Manual

## Getting Started Example

    from PySide.QtGui import QApplication
    from qtlayoutbuilder.api import Builder
    
    layouts = Builder.from_multiline_string("""
        my_page             QWidget
          layout            QHBoxLayout
            left            QGroupBox(Fruits)
              layout        QVBoxLayout
                label1      QLabel(Apple)
                label2      QLabel(Pear)
                label3      QLabel(Banana)
            middle          QGroupBox(Authors)
              layout        QVBoxLayout
                label1      QLabel(Dickens)
                label2      QLabel(Adams)
                label3      QLabel(Rowling)
            right_btn       QPushButton(Click me!)
    """
    
    # Access the objects created like this...
    the_button = layouts.get_element('my_page.layout.right_btn')
    
    app = QApplication()
    layouts.my_page.show()
    app.exec_()
    
       
This example creates a QWidget (which it calls *my_page*), and then sets its
layout to be a *QHBoxLayout*. Then it populates that layout with three items,
which it calls *left*, *middle*, and *right_btn*. The item called *left* is
specified as  QGroupBox, and will have its title set to *Fruits* - by calling 
*setTitle()* on it. The first item called *label1* will get the text *Apple*, by
calling *setText()* on it.

The example also shows how you can access the objects created afterwards.

## Anatomy of the Input Text
Each line of input creates an object of the type specified by the second word,
and provides the builder with a name to associate with it. The indentation of 
the first words specifies the parent-child hierarchy that the builder will 
create. Children are indented in relation to their parents by two spaces.

The indented alignment of the *name* words is of central importance. But there
is no significance in the alignment of the *type words*. They are lined up in
the example solely for readability. (See later section on auto-formatting)

## Parent / Child Relationships Supported
The builder implements Qt's existing system for parent child relationships by 
automatically adding items to layouts. But it goes further as you have already 
seen in the example input text above. The example showed how you can get it to
set the layout for a widget, and add text to suitable widgets.

The builder *'adds'* children to their *'parent'* using the following simple 
procedure.

### General Cases
First, it deals with the more general cases, by speculatively calling the following 
methods on the parent object with the child as a single argument. It stops at
the first one that works.

    addLayout(child)
    setLayout(child)
    addWidget(child)
    
> What we mean by *the first one that works*, is that the parent object has 
> such a method, and when that method is called with the child as a single 
> argument, it does not raise an exception.
    
If none of the above worked, it tries some methods intended for special cases as
follows. 
    
### Special case 1: addSpacerItem(child)
This is for adding a QSpacerItem child to a Q*BoxLayout like this:

    horiz       QHBoxLayout
      label1    QLabel('foo')
      spacer    QSpacerItem
      label1    QLabel('foo')
     
 The builder constructs the QSpacerItem with zero horizontal and vertical sizes,
 and it is thus exactly equivalent to calling addStretch() to the QHBoxLayout.
 
### Special case 2: addTab(child)

This is for adding tabs to a QTabWidget like this:

    tab_widget          QTabWidget
      first_tab         QWidget
      second_tab        QWidget
      third_tab         QWidget
      
 The builder names the tabs sequentially: tab_1, tab_2, ... tab_n
 
### Special case 3: setWidget(child)

This is for specifying the child QWidget for a QScrollArea like this:

    scroller            QScrollArea
      content           QWidget

> Note there are some parent child relationships that the builder cannot make
> completely automatically for you, because the arguments that must be provided
> to the *'add'* method cannot be guessed by the builder. An example would be
> adding the children to a QGridLayout - where the builder cannot know which
> rows and columns to specify.

> We could have extended the input file syntax to deal with some of these
> cases - but preferred to preserve the very simple, and quick to learn simple
> syntax.

> All is not lost however - see the later section about *Incomplete 
Hierarchies* below.

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
write it to. You can turn it on however by specifying a file it should 
write to:

    Builder.from_multiline_string(
            'the string', auto_format_and_write_to='my_file.txt')
    
## Error Handling
The builder handles all errors by raising an api.LayoutError which contains
an explanation and the offending line number from the input.

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

You can build multiple hierarchies like this:

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
    grid = layouts.get_element('page1.layout')
    cell = layouts.get_element('cell_widget'
    grid.addWidget(cell, 0, 1)
    
## Limitations
    
## Cautionary Notes
1. The builder is quite happy to let you set the layout on the types of 
widgets that you don't normally change the layout for. For example putting a 
QVBoxLayout on a QLabel. This is perfectly legal Qt and the builder does not 
attempt to second-guess whether you meant it or not. It's normally obvious when
you look at the result that the layout for that widget is screwed up.


