import keyboard

run = True
def action_clavier(event):
    global run
    if event.name == 'q':
        run = False
        