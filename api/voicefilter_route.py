from core.utils import * 
from core.log import logger
from models.voice_filter import predict_intent
from fuzzywuzzy import fuzz




router = APIRouter()

class VoiceFilterRequest(BaseModel):
    text: str
    role_code:str
    comp_code:str

@router.post("/voice_filter")
async def voice_filter(quest: VoiceFilterRequest):
    try:
        logger.info(f"Voice Input: {quest}")
        
        # Define bind parameters
        params = {
            'role_code': quest.role_code,
            'comp_code': quest.comp_code
        }

        # SQL to get menu data
        sql = """
        SELECT TO_CHAR(vc_menu_target) page_number,
               vc_module_code modul_ecode,
               vc_menu_object object_name,
               vc_menu_code manu_code,
               '' args,
               '' vc_field2
          FROM mk_menu_tree A
         WHERE lvl2 <= 1
           AND (VC_MODULE_CODE = '00' OR :role_code = '01'
                OR vc_menu_code IN (
                    SELECT vc_menu_Code
                      FROM MK_MENU_BASKET
                     WHERE vc_role_code = :role_code
                       AND vc_comp_code = :comp_code
                ))

        UNION

        SELECT TO_CHAR(VC_PAGE_NO) page_number,
               vc_module_code modul_ecode,
               vc_menu_object object_name,
               vc_menu_code manu_code,
               '' args,
               vc_field2
          FROM mk_module_menu A
         WHERE vc_mobile_version = 'Y'
           AND VC_PAGE_NO IS NOT NULL
           AND NVL(vc_field1, 'Y') <> 'N'
           AND (vc_menu_code = '00'
                OR :role_code = '01'
                OR (vc_module_code, vc_menu_code) IN (
                    SELECT vc_module_code,
                           SUBSTR(vc_menu_code, 3)
                      FROM mk_menu_basket
                     WHERE vc_role_code = :role_code
                       AND vc_comp_code = :comp_code
                ))
        """


        connection = connection_voice
        cursor = connection.cursor()
        cursor.execute(sql, params)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        data = [dict(zip(columns, row)) for row in rows]

        logger.info(f"Fetched {len(data)} menu items.")
        # logger.info(data)
        list_commands = [item['OBJECT_NAME'] for item in data]
        response = predict_intent(quest.text, list_commands)
        intent = response.get("Intent", "")
        if not intent:
            return JSONResponse(content={"message": "No intent identified"}, status_code=404)
        for item in data:
            if item['OBJECT_NAME'].strip().lower() == intent.strip().lower():
                print(item)
                return JSONResponse(content=item)

        return JSONResponse(content={"message": f"No exact match for intent: {intent}"}, status_code=500)

    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
