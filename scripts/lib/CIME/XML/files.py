"""
Interface to the config_files.xml file.  This class inherits from EntryID.py
"""
import re
from CIME.XML.standard_module_setup import *

from CIME.XML.entry_id import EntryID
from CIME.utils import expect, get_cime_root, get_model

logger = logging.getLogger(__name__)

class Files(EntryID):

    def __init__(self):
        """
        initialize an object

        >>> files = Files()
        >>> files.get_value('CASEFILE_HEADERS',resolved=False)
        '$CIMEROOT/config/config_headers.xml'
        """
        cimeroot = get_cime_root()
        infile = os.path.join(cimeroot, "config", get_model(), "config_files.xml")
        expect(os.path.isfile(infile), "Could not find or open file {}".format(infile))
        schema = os.path.join(cimeroot, "config", "xml_schemas", "entry_id.xsd")
        EntryID.__init__(self, infile, schema=schema)
        config_files_override = os.path.join(os.path.dirname(cimeroot),".config_files.xml")
        # .config_file.xml at the top level may overwrite COMP_ROOT_DIR_ nodes in config_files
        if os.path.isfile(config_files_override):
            self.read(config_files_override)
            self.overwrite_existing_entries()

    def get_value(self, vid, attribute=None, resolved=True, subgroup=None):
        value = super(Files, self).get_value(vid, attribute=attribute, resolved=False, subgroup=subgroup)
        if "COMP_ROOT_DIR" not in vid and value is not None and resolved and "COMP_ROOT_DIR" in value:
            m = re.search("(COMP_ROOT_DIR_[^/]+)/", value)
            comp_root_dir_var_name = m.group(1)
            comp_root_dir = self.get_value(comp_root_dir_var_name, attribute=attribute, resolved=False, subgroup=subgroup)
            self.set_value(comp_root_dir_var_name, comp_root_dir)
        if resolved and value is not None:
            value = self.get_resolved_value(value)

        return value

    def get_schema(self, nodename, attributes=None):
        node = self.get_optional_child("entry", {"id":nodename})
        schemanode = self.get_optional_child("schema", root=node, attributes=attributes)
        if schemanode is not None:
            logger.debug("Found schema for {}".format(nodename))
            return self.get_resolved_value(self.text(schemanode))
        return None

    def get_components(self, nodename):
        node = self.get_child("entry", {"id":nodename})
        vals = self.get_child("values", root=node)
        valnodes = self.get_children("value", root=vals)
        values = []
        for valnode in valnodes:
            value = self.get(valnode, "component")
            values.append(value)
        return values
