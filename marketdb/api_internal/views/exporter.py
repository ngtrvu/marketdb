from django.db import connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


from common.utils.datetime_util import VN_TIMEZONE, get_date_str
from common.utils.logger import logger
from api_internal.serializers.exporter import TableExporterSerializer
from utils.dj_exporter import DjExporter



class TableExporterView(APIView):
    def post(self, request, format=None):
        serializer = TableExporterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                table_name = serializer.data["table_name"]
                dataset_name = serializer.data["dataset_name"]
                bucket_name = serializer.data["bucket_name"]

                input_date = serializer.data.get("input_date")
                directory_name = serializer.data.get("directory_name", table_name)

                if not input_date:  # get default by today
                    input_date = get_date_str(date_format="%Y/%m/%d", tz=VN_TIMEZONE)
                
                success = DjExporter().export_table_to_gcs(
                    bucket_name=bucket_name,
                    dataset_name=dataset_name,
                    table_name=table_name,
                    directory_name=directory_name,
                    input_date=input_date,
                )

                if not success:
                    logger.warning(f"Export table {table_name} failed")
                    return Response(
                        {"error": "Export table failed"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                return Response(serializer.data, status=status.HTTP_200_OK)
            except Exception as ex:
                logger.warning(ex)
                return Response(
                    {"error": "Invalid input", "message": str(ex)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
