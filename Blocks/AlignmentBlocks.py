import logging
from .Utilities import *
from .Block import Block

class AlignmentBlock(Block):
    '''This class handles the flushright, flushleft
    and center environments'''

    @staticmethod
    def parse_env(parser, tex, parent_block, params):
        #we first create the Block
        block = AlignmentBlock(params['env'], tex, parent_block)
        logging.debug('AlignmentBlock.parse_env @ type: %s', params['env'])
        #now we parse the content
        children_blocks = parser.parse_instructions(tex, block, {})
        #now we can add the children nodes
        block.add_children_blocks(children_blocks)
        return block

    @staticmethod
    def parse_command(parser, tex, parent_block, params):
        block = AlignmentBlock(params['cmd'], '' , parent_block)
        logging.debug('AlignmentBlock.parse_cmd @ type: %s', params['cmd'])
        return (block,tex)


    def __init__(self, align_type, tex, parent_block):
        super().__init__(align_type, tex, parent_block)
        self.attributes['align_type'] = align_type

    def __str__(self):
        return '<Block:{}, ID:{}, alignment:{}>'.format(
            self.block_name, self.id, self.attributes['align_type'])


parser_hooks = {
    'flushleft' : AlignmentBlock.parse_env,
    'flushright' : AlignmentBlock.parse_env,
    'center' : AlignmentBlock.parse_env,
    'centering' : AlignmentBlock.parse_command
}
