const AWS = require('aws-sdk');
const sharp = require('sharp');
const s3 = new AWS.S3();

exports.handler = async (event) => {
    try {
        // Procesar el mensaje SNS
        const snsMessage = JSON.parse(event.Records[0].Sns.Message);
        const bucket = snsMessage.Records[0].s3.bucket.name;
        const key = decodeURIComponent(snsMessage.Records[0].s3.object.key.replace(/\+/g, ' '));
        
        // Verificar que es una imagen nueva en la carpeta uploads
        if (!key.startsWith('uploads/')) {
            console.log('No es una imagen en la carpeta uploads, ignorando');
            return;
        }

        // Obtener la imagen original
        const image = await s3.getObject({
            Bucket: bucket,
            Key: key
        }).promise();

        // Procesar la imagen en baja resolución (480px de ancho)
        const processedImage = await sharp(image.Body)
            .resize(480, null, {
                fit: 'inside',
                withoutEnlargement: true
            })
            .jpeg({ quality: 60 })
            .toBuffer();

        // Generar el nuevo nombre de archivo
        const newKey = key.replace('uploads/', process.env.LOW_RES_PREFIX + '/');

        // Guardar la imagen procesada
        await s3.putObject({
            Bucket: bucket,
            Key: newKey,
            Body: processedImage,
            ContentType: 'image/jpeg'
        }).promise();

        console.log(`Imagen procesada con éxito: ${newKey}`);
        return {
            statusCode: 200,
            body: JSON.stringify({
                message: 'Imagen procesada con éxito',
                key: newKey
            })
        };
    } catch (error) {
        console.error('Error procesando la imagen:', error);
        throw error;
    }
}; 