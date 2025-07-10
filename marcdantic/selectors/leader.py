class Leader:
    def __init__(self, leader: str):
        self._leader = leader

    @property
    def record_length(self) -> int:
        return int(self._leader[0:5].strip() or 0)

    @property
    def record_status(self) -> str:
        return self._leader[5:6].strip()

    @property
    def type_of_record(self) -> str:
        return self._leader[6:7].strip()

    @property
    def bibliographic_level(self) -> str:
        return self._leader[7:8].strip()

    @property
    def control_type(self) -> str:
        return self._leader[8:9].strip()

    @property
    def character_encoding_scheme(self) -> str:
        return self._leader[9:10].strip()

    @property
    def base_address_of_data(self) -> int:
        return int(self._leader[12:17].strip() or 0)

    @property
    def encoding_level(self) -> str:
        return self._leader[17:18].strip()

    @property
    def cataloging_form(self) -> str:
        return self._leader[18:19].strip()

    @property
    def multipart_resource_record_level(self) -> str:
        return self._leader[19:20].strip()

    @property
    def entry_map(self) -> str:
        return self._leader[20:24].strip()
