from flask import Flask, jsonify
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

app = Flask(__name__)

# Configure your S3 bucket name and AWS region
BUCKET_NAME = 'S3BUCKETNAME'
REGION_NAME = 'us-east-1'

# Initialize S3 client using boto3
s3 = boto3.client('s3', region_name=REGION_NAME)

@app.route('/list-bucket-content', defaults={'path': ''}, methods=['GET'])
@app.route('/list-bucket-content/<path:path>', methods=['GET'])
def list_bucket_content(path):
    try:
        # Ensure path ends with '/' to fetch the contents of directories properly
        prefix = path if path.endswith('/') or path == '' else f'{path}/'

        # Get objects under the given path
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix, Delimiter='/')

        # Prepare list of directories and files in the response
        contents = []

        # Common prefixes represent directories
        if 'CommonPrefixes' in response:
            contents.extend([prefix['Prefix'].rstrip('/') for prefix in response['CommonPrefixes']])

        # Contents represent files
        if 'Contents' in response:
            contents.extend([item['Key'][len(prefix):].rstrip('/') for item in response['Contents'] if item['Key'] != prefix])

        return jsonify({"content": contents})

    except NoCredentialsError:
        return jsonify({"error": "No AWS credentials found."}), 403
    except PartialCredentialsError:
        return jsonify({"error": "Incomplete AWS credentials."}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
    
