# User Manual

## Getting Started Example

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
    the_button = layouts.get_element('my_page.layout.right_btn')
    
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
indentation of the first word specifies the parent-child hierarchy that the 
builder will create. 

The **type word** on the right hand side will **usually** be one of the shortcut 
keywords as illustrated by the example. These refer to commonly used QLayouts 
and QWidgets. More details of this follow.

While the indented alignment of the *name* words is of central importance, there
is no significance to the alignment of the *type words*. They are lined up in
the example solely for readability.

## Parent / Child Relationships Supported
The builder appropriates Qt's existing notion of parent child relationships, but
has a much wider and looser interpretation of it - as you will see below.

The builder *'adds'* children to their *'parent'* using the following simple 
and 'dumb' procedure.

It speculatively calls the following methods on the parent object 
(in the order specified), and stops at the first one that works.

    addLayout(child)
    setLayout(child)
    addWidget(child)
    addTab(child)
    
> What we mean by *the first one that works*, is that the parent object has 
> such a method, and when that method is called with the child as a single 
> argument, it does not raise an exception.
    
This procedure allows:
*  Layout children to be added to layout parents
*  The layout to be set for a widget.
*  Widgets to be added to a Layout
*  Widgets to be added to a QStackedWidget
*  Widgets to be added to a QTabbedWidget

## Shortcut Keywords

The purpose of shortcut keywords is to minimise the typing required, and avoid
case-sensitivity for the frequently used Qt classes:

    hbox, vbox, label, button, stack, tabbed, group, widget, stretch
    
You can use the full Qt class names in their place. (Or specify any other 
QtGui class).

    layout            hbox
    layout            QHBoxLayout
    layout            QGridLayout       
    
> Note that the builder can only add children to parents for you automatically
> when one of the methods listed earlier, works when called with a **single**
> argument. (Which excludes QGridLayout for example). All is not lost 
> however - see the later section about *Incomplete Hierarchies* below.

> (The builder gets round this when calling *addTab* on a QTabbedWidget by 
> specifying the title for the tab using an automatically generated sequence.)

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
      
Using the capability to make multiple, separate hierarchies from the same input 
is useful for situations when the builder cannot automatically generate your 
tree all the way down (like if you use a QGridLayout). 

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
    grid = layouts.get_element('page1.layout')
    cell = layouts.get_element('cell_widget'
    grid.addWidget(cell, 0, 1)
