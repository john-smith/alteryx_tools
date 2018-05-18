import AlteryxPythonSDK as Sdk
import xml.etree.ElementTree as Et
import MeCab

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

        self.tagger = MeCab.Tagger('mecabrc')

    def ii_init(self, record_info_in: object) -> bool:
        self.record_info_in = record_info_in
        self.record_info_out = Sdk.RecordInfo(self.parent.alteryx_engine)

        self.record_info_out.add_field("record_id", Sdk.FieldType.int64)
        self.record_info_out.add_field("word", Sdk.FieldType.v_wstring, 65535)
        self.record_info_out.add_field("parts_of_speech", Sdk.FieldType.v_wstring, 255)

        self.parent.output_anchor.init(self.record_info_out)
        return True

    def ii_push_record(self, in_record: object) -> bool:
        id = self.record_info_in[self.record_info_in.get_field_num(self.parent.record_id)].get_as_int64(in_record)
        target = self.record_info_in[self.record_info_in.get_field_num(self.parent.target)].get_as_string(in_record)

        for item in self.tagger.parse(target).split("\n")[:-2] :
            item_split = item.split('\t')
            record_creator = self.record_info_out.construct_record_creator()
            self.record_info_out[self.record_info_out.get_field_num("record_id")].set_from_int64(record_creator, id)
            self.record_info_out[self.record_info_out.get_field_num("word")].set_from_string(record_creator, item_split[0])
            self.record_info_out[self.record_info_out.get_field_num("parts_of_speech")].set_from_string(record_creator, item_split[1])
            out_record = record_creator.finalize_record()
            self.parent.output_anchor.push_record(out_record)

        return True

    def ii_update_progress(self, d_percent: float):
        self.parent.alteryx_engine.output_tool_progress(self.parent.n_tool_id, d_percent)
        self.parent.output_anchor.update_progress(d_percent)

    def ii_close(self):
        self.parent.output_anchor.close()
