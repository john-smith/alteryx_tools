import AlteryxPythonSDK as Sdk
import xml.etree.ElementTree as Et
from janome.tokenizer import Tokenizer

class AyxPlugin:
    def __init__(self, n_tool_id: int, alteryx_engine: object, output_anchor_mgr: object):
        self.n_tool_id = n_tool_id
        self.alteryx_engine = alteryx_engine
        self.output_anchor_mgr = output_anchor_mgr

        self.output_anchor = None
        self.input = None

        self.target = None
        self.record_id = None

    def pi_init(self, str_xml: str):
        self.target = Et.fromstring(str_xml).find('target_field').text if 'target_field' in str_xml else None
        self.record_id = Et.fromstring(str_xml).find('record_id').text if 'record_id' in str_xml else None
        self.output_anchor = self.output_anchor_mgr.get_output_anchor('Output')

    def pi_add_incoming_connection(self, str_type: str, str_name: str) -> object:
        self.input = IncomingInterface(self)
        return self.input

    def pi_add_outgoing_connection(self, str_name: str) -> bool:
        return True

    def pi_push_all_records(self, n_record_limit: int) -> bool:
        self.alteryx_engine.output_message(self.n_tool_id, Sdk.EngineMessageType.error, 'Missing Incoming Connection')
        return False

    def pi_close(self, b_has_errors: bool):
        self.output_anchor.assert_close()

class IncomingInterface:
    def __init__(self, parent: object):
        self.parent = parent
        self.record_info_in = None
        self.record_info_out = None

        self.tokenizer = Tokenizer()

    def ii_init(self, record_info_in: object) -> bool:
        self.record_info_in = record_info_in
        self.record_info_out = Sdk.RecordInfo(self.parent.alteryx_engine)

        self.record_info_out.add_field(self.parent.record_id, Sdk.FieldType.int64)
        self.record_info_out.add_field("surface", Sdk.FieldType.v_wstring, 65535)
        self.record_info_out.add_field("part_of_speech", Sdk.FieldType.v_wstring, 255)
        self.record_info_out.add_field("part_of_speech1", Sdk.FieldType.v_wstring, 255)
        self.record_info_out.add_field("part_of_speech2", Sdk.FieldType.v_wstring, 255)
        self.record_info_out.add_field("part_of_speech3", Sdk.FieldType.v_wstring, 255)
        self.record_info_out.add_field("infl_type", Sdk.FieldType.v_wstring, 255)
        self.record_info_out.add_field("infl_form", Sdk.FieldType.v_wstring, 255)
        self.record_info_out.add_field("base_form", Sdk.FieldType.v_wstring, 65535)
        self.record_info_out.add_field("reading", Sdk.FieldType.v_wstring, 65535)
        self.record_info_out.add_field("phonetic", Sdk.FieldType.v_wstring, 65535)

        self.parent.output_anchor.init(self.record_info_out)
        return True

    def ii_push_record(self, in_record: object) -> bool:
        id = self.record_info_in[self.record_info_in.get_field_num(self.parent.record_id)].get_as_int64(in_record)
        target = self.record_info_in[self.record_info_in.get_field_num(self.parent.target)].get_as_string(in_record)

        for token in self.tokenizer.tokenize(target):
            record_creator = self.record_info_out.construct_record_creator()
            self.record_info_out[self.record_info_out.get_field_num(self.parent.record_id)].set_from_int64(record_creator, id)
            self.record_info_out[self.record_info_out.get_field_num("surface")].set_from_string(record_creator, token.surface)

            pos, pos1, pos2, pos3 = token.part_of_speech.split(',')
            self.record_info_out[self.record_info_out.get_field_num("part_of_speech")].set_from_string(record_creator, pos)
            self.record_info_out[self.record_info_out.get_field_num("part_of_speech1")].set_from_string(record_creator, pos1)
            self.record_info_out[self.record_info_out.get_field_num("part_of_speech2")].set_from_string(record_creator, pos2)
            self.record_info_out[self.record_info_out.get_field_num("part_of_speech3")].set_from_string(record_creator, pos3)

            self.record_info_out[self.record_info_out.get_field_num("infl_type")].set_from_string(record_creator, token.infl_type)
            self.record_info_out[self.record_info_out.get_field_num("infl_form")].set_from_string(record_creator, token.infl_form)
            self.record_info_out[self.record_info_out.get_field_num("base_form")].set_from_string(record_creator, token.base_form)
            self.record_info_out[self.record_info_out.get_field_num("reading")].set_from_string(record_creator, token.reading)
            self.record_info_out[self.record_info_out.get_field_num("phonetic")].set_from_string(record_creator, token.phonetic)

            out_record = record_creator.finalize_record()
            self.parent.output_anchor.push_record(out_record)

        return True

    def ii_update_progress(self, d_percent: float):
        self.parent.alteryx_engine.output_tool_progress(self.parent.n_tool_id, d_percent)
        self.parent.output_anchor.update_progress(d_percent)

    def ii_close(self):
        self.parent.output_anchor.close()
