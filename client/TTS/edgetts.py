import asyncio
import math
import os
import random
from typing import List

import edge_tts
from aiohttp import ClientConnectorError
from rich.progress import track

from utils import settings
from utils.voice import getduration

# edge-tts --rate=-50% --text "Hello, world!" --write-media hello_with_rate_halved.mp3

voices = {
    "en-AU-NatashaNeural",
    "en-AU-WilliamNeural",
    "en-CA-ClaraNeural",
    "en-CA-LiamNeural",
    "en-HK-SamNeural",
    "en-HK-YanNeural",
    "en-IN-NeerjaNeural",
    "en-IN-PrabhatNeural",
    "en-IE-ConnorNeural",
    "en-IE-EmilyNeural",
    "en-KE-AsiliaNeural",
    "en-KE-ChilembaNeural",
    "en-NZ-MitchellNeural",
    "en-NZ-MollyNeural",
    "en-NG-AbeoNeural",
    "en-NG-EzinneNeural",
    "en-PH-JamesNeural",
    "en-PH-RosaNeural",
    "en-SG-LunaNeural",
    "en-SG-WayneNeural",
    "en-ZA-LeahNeural",
    "en-ZA-LukeNeural",
    "en-TZ-ElimuNeural",
    "en-TZ-ImaniNeural",
    "en-GB-LibbyNeural",
    "en-GB-MaisieNeural",
    "en-GB-RyanNeural",
    "en-GB-SoniaNeural",
    "en-GB-ThomasNeural",
    "en-US-AriaNeural",
    "en-US-AnaNeural",
    "en-US-ChristopherNeural",
    "en-US-EricNeural",
    "en-US-GuyNeural",
    "en-US-JennyNeural",
    "en-US-MichelleNeural",
    "en-US-RogerNeural",
    "en-US-SteffanNeural",
    "af-ZA-AdriNeural",
    "af-ZA-WillemNeural",
    "am-ET-AmehaNeural",
    "am-ET-MekdesNeural",
    "ar-AE-FatimaNeural",
    "ar-AE-HamdanNeural",
    "ar-BH-AliNeural",
    "ar-BH-LailaNeural",
    "ar-DZ-AminaNeural",
    "ar-DZ-IsmaelNeural",
    "ar-EG-SalmaNeural",
    "ar-EG-ShakirNeural",
    "ar-IQ-BasselNeural",
    "ar-IQ-RanaNeural",
    "ar-JO-SanaNeural",
    "ar-JO-TaimNeural",
    "ar-KW-FahedNeural",
    "ar-KW-NouraNeural",
    "ar-LB-LaylaNeural",
    "ar-LB-RamiNeural",
    "ar-LY-ImanNeural",
    "ar-LY-OmarNeural",
    "ar-MA-JamalNeural",
    "ar-MA-MounaNeural",
    "ar-OM-AbdullahNeural",
    "ar-OM-AyshaNeural",
    "ar-QA-AmalNeural",
    "ar-QA-MoazNeural",
    "ar-SA-HamedNeural",
    "ar-SA-ZariyahNeural",
    "ar-SY-AmanyNeural",
    "ar-SY-LaithNeural",
    "ar-TN-HediNeural",
    "ar-TN-ReemNeural",
    "ar-YE-MaryamNeural",
    "ar-YE-SalehNeural",
    "az-AZ-BabekNeural",
    "az-AZ-BanuNeural",
    "bg-BG-BorislavNeural",
    "bg-BG-KalinaNeural",
    "bn-BD-NabanitaNeural",
    "bn-BD-PradeepNeural",
    "bn-IN-BashkarNeural",
    "bn-IN-TanishaaNeural",
    "bs-BA-GoranNeural",
    "bs-BA-VesnaNeural",
    "ca-ES-EnricNeural",
    "ca-ES-JoanaNeural",
    "cs-CZ-AntoninNeural",
    "cs-CZ-VlastaNeural",
    "cy-GB-AledNeural",
    "cy-GB-NiaNeural",
    "da-DK-ChristelNeural",
    "da-DK-JeppeNeural",
    "de-AT-IngridNeural",
    "de-AT-JonasNeural",
    "de-CH-JanNeural",
    "de-CH-LeniNeural",
    "de-DE-AmalaNeural",
    "de-DE-ConradNeural",
    "de-DE-KatjaNeural",
    "de-DE-KillianNeural",
    "el-GR-AthinaNeural",
    "el-GR-NestorasNeural",
    "es-AR-ElenaNeural",
    "es-AR-TomasNeural",
    "es-BO-MarceloNeural",
    "es-BO-SofiaNeural",
    "es-CL-CatalinaNeural",
    "es-CO-GonzaloNeural",
    "es-CL-LorenzoNeural",
    "es-CO-SalomeNeural",
    "es-CR-JuanNeural",
    "es-CR-MariaNeural",
    "es-CU-BelkysNeural",
    "es-CU-ManuelNeural",
    "es-DO-EmilioNeural",
    "es-DO-RamonaNeural",
    "es-EC-AndreaNeural",
    "es-EC-LuisNeural",
    "es-ES-AlvaroNeural",
    "es-ES-ElviraNeural",
    "es-GQ-JavierNeural",
    "es-GQ-TeresaNeural",
    "es-GT-AndresNeural",
    "es-GT-MartaNeural",
    "es-HN-CarlosNeural",
    "es-HN-KarlaNeural",
    "es-MX-DaliaNeural",
    "es-MX-JorgeNeural",
    "es-NI-FedericoNeural",
    "es-NI-YolandaNeural",
    "es-PA-MargaritaNeural",
    "es-PA-RobertoNeural",
    "es-PE-AlexNeural",
    "es-PE-CamilaNeural",
    "es-PR-KarinaNeural",
    "es-PR-VictorNeural",
    "es-PY-MarioNeural",
    "es-PY-TaniaNeural",
    "es-SV-LorenaNeural",
    "es-SV-RodrigoNeural",
    "es-US-AlonsoNeural",
    "es-US-PalomaNeural",
    "es-UY-MateoNeural",
    "es-UY-ValentinaNeural",
    "es-VE-PaolaNeural",
    "es-VE-SebastianNeural",
    "et-EE-AnuNeural",
    "et-EE-KertNeural",
    "fa-IR-DilaraNeural",
    "fa-IR-FaridNeural",
    "fi-FI-HarriNeural",
    "fi-FI-NooraNeural",
    "fil-PH-AngeloNeural",
    "fil-PH-BlessicaNeural",
    "fr-BE-CharlineNeural",
    "fr-BE-GerardNeural",
    "fr-CA-AntoineNeural",
    "fr-CA-JeanNeural",
    "fr-CA-SylvieNeural",
    "fr-CH-ArianeNeural",
    "fr-CH-FabriceNeural",
    "fr-FR-DeniseNeural",
    "fr-FR-EloiseNeural",
    "fr-FR-HenriNeural",
    "ga-IE-ColmNeural",
    "ga-IE-OrlaNeural",
    "gl-ES-RoiNeural",
    "gl-ES-SabelaNeural",
    "gu-IN-DhwaniNeural",
    "gu-IN-NiranjanNeural",
    "he-IL-AvriNeural",
    "he-IL-HilaNeural",
    "hi-IN-MadhurNeural",
    "hi-IN-SwaraNeural",
    "hr-HR-GabrijelaNeural",
    "hr-HR-SreckoNeural",
    "hu-HU-NoemiNeural",
    "hu-HU-TamasNeural",
    "id-ID-ArdiNeural",
    "id-ID-GadisNeural",
    "is-IS-GudrunNeural",
    "is-IS-GunnarNeural",
    "it-IT-DiegoNeural",
    "it-IT-ElsaNeural",
    "it-IT-IsabellaNeural",
    "ja-JP-KeitaNeural",
    "ja-JP-NanamiNeural",
    "jv-ID-DimasNeural",
    "jv-ID-SitiNeural",
    "ka-GE-EkaNeural",
    "ka-GE-GiorgiNeural",
    "kk-KZ-AigulNeural",
    "kk-KZ-DauletNeural",
    "km-KH-PisethNeural",
    "km-KH-SreymomNeural",
    "kn-IN-GaganNeural",
    "kn-IN-SapnaNeural",
    "ko-KR-InJoonNeural",
    "ko-KR-SunHiNeural",
    "lo-LA-ChanthavongNeural",
    "lo-LA-KeomanyNeural",
    "lt-LT-LeonasNeural",
    "lt-LT-OnaNeural",
    "lv-LV-EveritaNeural",
    "lv-LV-NilsNeural",
    "mk-MK-AleksandarNeural",
    "mk-MK-MarijaNeural",
    "ml-IN-MidhunNeural",
    "ml-IN-SobhanaNeural",
    "mn-MN-BataaNeural",
    "mn-MN-YesuiNeural",
    "mr-IN-AarohiNeural",
    "mr-IN-ManoharNeural",
    "ms-MY-OsmanNeural",
    "ms-MY-YasminNeural",
    "mt-MT-GraceNeural",
    "mt-MT-JosephNeural",
    "my-MM-NilarNeural",
    "my-MM-ThihaNeural",
    "nb-NO-FinnNeural",
    "nb-NO-PernilleNeural",
    "ne-NP-HemkalaNeural",
    "ne-NP-SagarNeural",
    "nl-BE-ArnaudNeural",
    "nl-BE-DenaNeural",
    "nl-NL-ColetteNeural",
    "nl-NL-FennaNeural",
    "nl-NL-MaartenNeural",
    "pl-PL-MarekNeural",
    "ps-AF-GulNawazNeural",
    "ps-AF-LatifaNeural",
    "pt-BR-AntonioNeural",
    "pt-BR-FranciscaNeural",
    "pt-PT-DuarteNeural",
    "pt-PT-RaquelNeural",
    "ro-RO-AlinaNeural",
    "ro-RO-EmilNeural",
    "ru-RU-DmitryNeural",
    "ru-RU-SvetlanaNeural",
    "si-LK-SameeraNeural",
    "si-LK-ThiliniNeural",
    "sk-SK-LukasNeural",
    "sk-SK-ViktoriaNeural",
    "sl-SI-PetraNeural",
    "sl-SI-RokNeural",
    "so-SO-MuuseNeural",
    "so-SO-UbaxNeural",
    "tr-TR-EmelNeural",
    "sq-AL-AnilaNeural",
    "sq-AL-IlirNeural",
    "sr-RS-NicholasNeural",
    "sr-RS-SophieNeural",
    "su-ID-JajangNeural",
    "su-ID-TutiNeural",
    "sv-SE-MattiasNeural",
    "sv-SE-SofieNeural",
    "sw-KE-RafikiNeural",
    "sw-KE-ZuriNeural",
    "sw-TZ-DaudiNeural",
    "sw-TZ-RehemaNeural",
    "ta-IN-PallaviNeural",
    "ta-IN-ValluvarNeural",
    "ta-LK-KumarNeural",
    "ta-LK-SaranyaNeural",
    "ta-MY-KaniNeural",
    "ta-MY-SuryaNeural",
    "ta-SG-AnbuNeural",
    "ta-SG-VenbaNeural",
    "te-IN-MohanNeural",
    "te-IN-ShrutiNeural",
    "th-TH-NiwatNeural",
    "th-TH-PremwadeeNeural",
    "tr-TR-AhmetNeural",
    "uk-UA-OstapNeural",
    "uk-UA-PolinaNeural",
    "ur-IN-GulNeural",
    "ur-IN-SalmanNeural",
    "ur-PK-AsadNeural",
    "ur-PK-UzmaNeural",
    "uz-UZ-MadinaNeural",
    "uz-UZ-SardorNeural",
    "vi-VN-HoaiMyNeural",
    "vi-VN-NamMinhNeural",
    "zh-CN-XiaoxiaoNeural",
    "pl-PL-ZofiaNeural",
    "zh-CN-XiaoyiNeural",
    "zh-CN-YunjianNeural",
    "zh-CN-YunxiNeural",
    "zh-CN-YunxiaNeural",
    "zh-CN-YunyangNeural",
    "zh-CN-liaoning-XiaobeiNeural",
    "zh-CN-shaanxi-XiaoniNeural",
    "zh-HK-HiuGaaiNeural",
    "zh-HK-HiuMaanNeural",
    "zh-HK-WanLungNeural",
    "zh-TW-HsiaoChenNeural",
    "zh-TW-HsiaoYuNeural",
    "zh-TW-YunJheNeural",
    "zu-ZA-ThandoNeural",
    "zu-ZA-ThembaNeural",
}


class edge:
    """
    Class for edge TTS
    """

    def __init__(self) -> None:
        self.max_chars: int = 10**5
        self.voices = voices
        self.start_padding: float = 0
        self.startings: list[int] = []
        self.endings: list[int] = []
        # self.offsets:List[Tuple]    = []
        self.texts: List[str] = []
        self.has_sub = True

    def run(self, text, filepath, random_voice: bool = False) -> None:
        for _ in range(5):
            try:
                asyncio.new_event_loop().run_until_complete(
                    self._main(text, filepath, random_voice)
                )
                break
            except ClientConnectorError:
                print("handling error")
                continue

    async def _main(self, text, filepath, random_voice: bool = False) -> None:
        if random_voice:
            voice = self.randomvoice()
        else:
            if not settings.config["settings"]["tts"]["edge_voice"]:
                raise ValueError(
                    f"Please set the config variable edge voice to a valid voice. options are: {voices}"
                )
        voice = settings.config["settings"]["tts"]["edge_voice"]

        speed = f'+{settings.config["settings"]["tts"]["edge_speed"]}%'
        communicate = edge_tts.Communicate(text, voice, rate=speed)
        startings: list[int] = []
        endings: list[int] = []
        texts = []
        with open(filepath, "wb") as file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    # self.offsets.append((chunk["offset"],chunk["duration"]))
                    start = chunk["offset"] + (self.start_padding)
                    startings.append(start)
                    endings.append(start + chunk["duration"])
                    texts.append(chunk["text"])

        if settings.config["settings"]["style"] == 0:
            self.make_ass(startings, endings, texts, filepath)

        self.update_last_time(filepath)

    def update_last_time(self, filename):
        """
        Update last time stamp so next time stamp will be after the prev

        """
        self.start_padding += getduration(filename) * 10**7
        # self.endings[-1].

    def make_ass(self, startings, endings, texts, name: str) -> None:
        """

        Makes the ASS file with current voice durtaion and text

        """
        file_data = ""
        file_data += "[Script Info]\n"
        file_data += "Title: My Subtitle\n"
        file_data += "ScriptType: v4.00+\n"
        file_data += f'PlayResX: {settings.config["settings"]["resolution_w"]}\n'
        file_data += f'PlayResY: {settings.config["settings"]["resolution_h"]}\n'
        file_data += "\n"
        file_data += "[V4+ Styles]\n"
        file_data += "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
        file_data += f'Style: Default,Carter One,{settings.config["fonts"]["single_word_font_size"]},     &Hffffff,       &H00000000,       &H00000000          ,&H0,        0,      0,     0,  0,      100,      100,      0,     0,      1,   3,   0,    10,10,10,10,1\n'
        file_data += "\n"
        file_data += "[Events]\n"
        file_data += "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"

        len_text = len(texts)
        for i in range(len_text):
            if not (i == 0 or i == (len_text - 1)):
                start_time = self.mktimestamp(startings[i])
                end_time = self.mktimestamp(startings[i + 1] - 10)
            else:
                start_time = self.mktimestamp(startings[i])
                end_time = self.mktimestamp(endings[i])

            file_data += (
                f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,"
                + "{\\an5\\fscx90\\fscy90\\t(0,150,\\fscx100\\fscy100)}"
                + f"{texts[i].upper()}\n"
            )

        with open(self.prepare_name(name) + ".ass", "w", encoding="utf-8") as f:
            f.write(file_data)

    def randomvoice(self) -> str:
        return random.choice(self.voices)

    @staticmethod
    def prepare_name(name: str) -> str:
        """
        Remove ``.mp3'`` at end of file name
        """

        if name.endswith(".mp3"):
            name, _ = os.path.splitext(name)
            return name
        raise

    @staticmethod
    def mktimestamp(time_unit: float) -> str:
        """
        mktimestamp returns the timecode of the subtitle.

        The timecode is in the format of 00:00:00.000.

        Returns:
            str: The timecode of the subtitle.
        """
        hour = math.floor(time_unit / 10**7 / 3600)
        minute = math.floor((time_unit / 10**7 / 60) % 60)
        seconds = (time_unit / 10**7) % 60
        return f"{hour:01d}:{minute:02d}:{seconds:06.2f}"
