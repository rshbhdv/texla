from log import *
import json
import yaml
from texla.Parser import Parser
from texla.Renderers.MediaWikiRenderer import MediaWikiRenderer
import texla.PageTree.Exporter as exporter
from texla.Exceptions.TexlaExceptions import *
from texla.Reporter import Reporter


def execute_texla_mediawiki(config):
    p = Parser(config)
    a = open(config['input_path'], 'r').read()
    try:
        tree = p.parse(a)
    except (PreparserError, ParserError) as err:
        err.print_error()
        exit()
    f = open(config['output_path'] + '.tree', 'w')
    json_tree = tree.to_json(0)
    n_blocks = tree.n_blocks()
    logging.info('PARSED %i Blocks', n_blocks)
    f.write(json_tree)
    logging.info('\033[0;34m############### STARTING RENDERING ###############\033[0m')
    #creating Reporter
    reporter = Reporter(p.tree_explorer)
    #rendering
    rend = MediaWikiRenderer(config, reporter)
    rend.start_rendering(tree)
    o = open(config['output_path'] + '.json', 'w')
    o.write(json.dumps(rend.tree.get_tree_json(), indent=3))
    #print page tree before POST-PROCESSING
    logging.info('PageTree:\n'+rend.tree.get_tree_debug())
    #collpasing
    logging.info('\033[0;34m############### STARTING POST-PROCESSING ###############\033[0m')
    tree = rend.tree
    tree.collapse_tree(config['collapse_content_level'],
                       config['collapse_pages_level'])
    #printing tree after POST-PROCESSING
    logging.info('PageTree:\n'+rend.tree.get_tree_debug())
    oc = open(config['output_path'] + '-coll.json', 'w')
    oc.write(json.dumps(rend.tree.get_tree_json(), indent=3))
    logging.info('\033[0;34m############### EXPORTING ###############\033[0m')
    if config['create_index']:
        tree.create_indexes(config["export_book_page"])
    exporter.exportPages(tree.pages, config['output_path'] + '.mw',
                         config['export_format'])
    if config['export_single_pages']:
        exporter.export_singlePages(tree.pages,
                                    config['output_path'] + '_pages',
                                    config['export_format'])
    if config['export_pages_tree']:
        exporter.export_pages_tree(tree.pages.values(),
                                   config['output_path'] + "_pages")
    reporter.print_report(console=True)
    logging.info('Finished')


if __name__ == '__main__':
    #reading JSON configs
    config = yaml.load(open('configs.yaml','r'))
    #loading localized keywords
    config['keywords'] = yaml.load(open('i18n.yaml','r'))[config['lang']]
    #executing process for alla renderers
    if config['renderer'] == 'mediawiki':
        execute_texla_mediawiki(config)
