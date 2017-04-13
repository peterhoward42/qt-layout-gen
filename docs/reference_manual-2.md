# User Manual

## Reference Example

    from PySide.QtGui import QApplication
    from qtlayoutbuilder.api import Builder
    
    layouts = Builder.from_multiline_string("""
        my_page             widget
          layout            hbox
            left            group(Fruits)
              layout        vbox
                label1      label(Apple)
                label2      label(Pear)
                label3      label(Banana)
            middle          group(Authors)
              layout        vbox
                label1      label(Dickens)
                label2      label(Adams)
                label3      label(Rowling)
            right_btn       button(Click me!)
    """
    
    # Access the objects created like this...
    the_button = layouts.my_page.right_btn
    
    app = QApplication()
    layouts.my_page.show()
    app.exec_()
    
       
This example creates a QWidget (which it calls *my_page*), and then sets its
layout to be a *QHBoxLayout*. Then it populates that layout with three items,
which it calls *left*, *middle*, and *right_btn*. The item called *left* is
specified as  QGroupBox, and it will get the text *Fruits* - by calling 
*setText()* on it.

The example also shows how you can access the objects created afterwards.

## Anatomy of the Input Text
Each line of input creates an object of the type specified by the second word,
and gives that object the name specified by the first word. The relative 
indentation of the first word specifies a (very loosely defined) 
parent-child hierarchy that the builder will create. 

The **type word** on the right will **usually** be one of the shortcut 
keywords as illustrated by the example. These refer to commonly used QLayouts 
and QWidgets. More details of this follow.

## Parent / Child Relationships Supported
The builder adds children to their parent using a simple and 'dumb' procedure.
It speculatively calls the following methods on the parent object 
(in the order specified), and stops at the first one that works.

    addLayout(child)
    setLayout(child)
    addWidget(child)
    addTab(child)
    
> What we mean by *the first method that works*, is: the parent object has 
> such a method, and when that method is called with the child as a single 
> argument, it does not raise an exception.
    
This procedure allows:
*  Layout children to be added to layout parents
*  The layout to be set for a widget.
*  Widgets to be added to a Layout
*  Widgets to be added to a QStackedWidget
*  Widgets to be added to a QTabbedWidget

## Shortcut Keywords

The shortcut keywords aim to reduce typing and to prevent the need to 
think about case-sensitivity of the Qt class names.

todo - make sure these agree with code and list is complete.

    hbox, vbox, label, button, stack, tabbed, group, widget, stretch
    
You can use the full Qt class names in their place. (Or any other Qt class).

    layout            hbox
    layout            QHBoxLayout
    layout            QGridLayout       
    
> Note that the builder can only add children to parents for you automatically
> when one of the methods listed earlier, works when called with a single 
> argument. (Unlike QGridLayout). All is not lost however - see the later 
> section XXXX.

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
    
> It does this with the help of Python's garbage collector - which knows about
> every object that exists in your program.
    
## Setting the Text on Things
Anytime you put something in parenthesis after a type word like this:

    label1      label(some text)
    
The builder will call setText('some text') on the parent object.
   
## Taking the Input From a File

    layouts = Builder.from_file(file_path)
    
This variant has a couple of practical advantages, particularly during 
iterative development. Firstly, the line numbers in the error reporting are 
more directly useful. But it also offers the capability to write back out
your file (over-writing the original), having automatically aligned the right 
column to just beyond the longest name entry present. This is considerably
easier than bothering to maintain this manually. Nb. the right aligment of
the *type* column is only a visual aid - it is not necessary syntactically.

    layouts = Builder.from_file(file_path, write_back_out=True)
    
Your original file variants are not lost, they are saved in a temporary directory - as
detailed (to stdout) when using this mode.

## Error Handling
The builder handles all errors by raising an api.LayoutError which contains
an explanation and the offending line number from the input.

    try:
        Builder.xxx()
    except LayoutError as e:
        print str(e)

## Comments

    # I am a comment
    layouts = Builder.from_multiline_string("""
        my_page             widget # ME TOO !
          layout            hbox
          
## Incomplete or Multiple Hierarchies

You can build multiple hierarchies like this:

    page1       widget
      layout    vbox
      etc...
    page2       widget
      layout    vbox
      etc...
      
If you incorporate an object into your hierarchy that the builder cannot
recursively continue to populate with children (like the QGridLayout for 
example). You can anticipate doing that bit externally afterwards, but continue
to build the tree below that discontinuity.

    layouts = Builder.from_multiline_string("""
        page1       widget
          layout    QGridLayout
          # Cannot go any further because need row/column to add children :-(
      
        # We can still make the things to go into the grid.
        cell_widget widget
          layout    vbox
            label1  label(foo)
            label2  label(bar)
            label3  label(baz)
    """
    
    # And then access the objects to finish the job.
    layouts.page1.layout.addWidget(layouts.cell_widget, 0, 1)

