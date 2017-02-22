from ..Parser import Blocks
from ..Parser.TreeExplorer import TreeExplorer
import logging
import importlib

class Renderer():
    def __init__(self, reporter):
        self.reporter = reporter
        #hooks implemented directly by the Renderer class.
        self.render_hooks = {}
        #plugins hooks
        self.pre_render_hooks = {}
        self.post_render_hooks = {}
        self.start_hooks = []
        self.end_hooks = []
        self.loaded_plugins = {}
        self.tree_explorer = None

    def register_plugins(self, plugins):
        for plugin in plugins:
            module = importlib.import_module("..plugins"+'.'+ plugin, __name__)
            if hasattr(module, "plugin_render_hooks"):
                self.loaded_plugins[plugin] = module
                self.register_render_plugin_hooks(module.plugin_render_hooks)
                logging.debug("Renderer.register_plugins "\
                             "@ Loaded plugin: {}".format(plugin))
                logging.debug("Plugin {} render hooks: {}".format( plugin,
                            list(module.plugin_render_hooks.keys())))
            if hasattr(module, "plugin_lifecycle_hooks"):
                self.register_lifecyle_plugin_hooks(module.plugin_lifecycle_hooks)
                logging.debug("Plugin {} lifecycle hooks: {}".format( plugin,
                            list(module.plugin_lifecycle_hooks.keys())))



    def register_render_plugin_hooks(self, hooks):
        '''This function registers the hooks for renderer plugins.
        The plugins can define hooks for pre and post render actions.
        The pre hook receives the block before the rendering and can
        only return the block itself, modified.
        The post hook receive the block and the text from the renderer:
        it has to return the final text only.
        The keyword ALL creates a hooks for all the blocks.
        Note that it is always called after all the other hooks.'''
        for bl in hooks:
            if "pre" in hooks[bl]:
                self.register_pre_renderer_hook(bl, hooks[bl]["pre"])
            if "post" in hooks[bl]:
                self.register_post_renderer_hook(bl, hooks[bl]["post"])
        #checking ALL keyword
        if "ALL" in hooks:
            if "pre" in hooks["ALL"]:
                self.register_pre_renderer_hook(bl, hooks["ALL"]["pre"])
            if "post" in hooks["ALL"]:
                self.register_post_renderer_hook(bl, hooks["ALL"]["post"])

    def register_lifecyle_plugin_hooks(self, hooks):
        ''' This function registers the hooks for the renderer lifecycle.
        Plugins can register hooks for the start and end actions.
        The start hook is called with the root_block of the chain.
        The end hook is called without arguments. These hooks must be used
        only to signal the actions to the plugins.'''
        if "start" in hooks:
            self.register_start_hook(hooks["start"])
        if "end" in hooks:
            self.register_end_hook(hooks["end"])

    def register_pre_renderer_hook(self, block, hook):
        if block not in self.pre_render_hooks:
            self.pre_render_hooks[block] = []
        self.pre_render_hooks[block].append(hook)

    def register_post_renderer_hook(self, block, hook):
        if block not in self.post_render_hooks:
            self.post_render_hooks[block] = []
        self.post_render_hooks[block].append(hook)

    def register_start_hook(self, hook):
        self.start_hooks.append(hook)

    def register_end_hook(self, hook):
        self.end_hooks.append(hook)

    def start_rendering(self, root_block):
        '''This function create a TreeExplorer instance
        and passes it to the plugin that has the variable
        needs_tree_explorer=True. Then it starts the plugins'''
        self.tree_explorer = TreeExplorer(root_block)
        #passing the tree_explorer
        for pl in self.loaded_plugins.values():
            if hasattr(pl, "needs_tree_explorer"):
                if pl.needs_tree_explorer:
                    logging.debug("Renderer @ Inserting "\
                                  "TreeExplorer into plugin {}".format(pl))
                    pl.tree_explorer = self.tree_explorer
        #starting the plugins
        for hook in self.start_hooks:
            hook(root_block)

    def end_rendering(self):
        #ending plugins
        for hook in self.end_hooks:
            hook()

    def render_children_blocks(self, block, collapse=True):
        '''This is one of the most important funciont
        of the rendering process.
        This function takes all the children blocks of
        a block and get they rendering output.
        If collapsed=True it returns a unique string,
        otherwise it returns a list of tuples with[(block_name, output)]
        '''
        output = []
        for bl in block.ch_blocks:
            #it's not necessary checking for renderer_hook
            #because default hook is mandatory
            output.append((bl.block_name, self.render_block(bl)))
        if collapse:
            return ''.join([x[1] for x in output])
        else:
            return output

    def render_block(self, bl):
        '''This function calls the right render_hook for
        the block. If there isn't an hook it calld the default,
        that is mandatory'''
        output = ""
        ######### pre hooks ############
        #hooks executed in the order of inserction
        #They receive the block and they can only modify the block object
        if bl.block_name in self.pre_render_hooks:
            for prehook in self.pre_render_hooks[bl.block_name]:
                #calling prehook with the block
                prehook(bl)
        #calling after the others the ALL hooks
        if "ALL" in self.pre_render_hooks:
            for prehook in self.pre_render_hooks["ALL"]:
                #calling prehook with the block
                prehook(bl)
        ######## rendering #############
        if bl.block_name in self.render_hooks:
            logging.debug('Render @ block: ' + bl.block_name)
            output = self.render_hooks[bl.block_name](bl)
        else:
            #default hook is mandatory
            logging.debug('Render @ block: default@' + bl.block_name)
            #reporting to the Reporter
            if bl.block_name != "default":
                self.reporter.add_not_rendered_block(bl)
            output = self.render_hooks['default'](bl)
        ######## post hooks ###########
        #hooks executed in the order of inserction.
        #They receive the block and text. They have to return the
        #output text, that is passed to the next posthook
        if bl.block_name in self.post_render_hooks:
            for posthook in self.post_render_hooks[bl.block_name]:
                #calling posthook with the block and output
                output = posthook(bl, output)
        #calling ALL hooks after the others
        if "ALL" in self.post_render_hooks:
            for posthook in self.post_render_hooks["ALL"]:
                #calling posthook with the block and output
                output = posthook(bl, output)
        #final output
        return output


    def render_blocks(self, bls, collapse=False):
        '''This function renderes a list of blocks.
        It's the same as render_children_blocks but
        with a generic list'''
        output = []
        for bl in bls:
            output.append((bl.block_name,self.render_block(bl)))
        if collapse:
            return ''.join([x[1] for x in output])
        else:
            return output
