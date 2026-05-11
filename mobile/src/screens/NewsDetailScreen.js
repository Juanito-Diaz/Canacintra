import React, { useState, useEffect, useContext } from 'react';
import { View, Text, StyleSheet, Image, ScrollView, TextInput, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import client from '../api/client';
import { AuthContext } from '../context/AuthContext';

const NewsDetailScreen = ({ route }) => {
    const { news } = route.params;
    const { user, token } = useContext(AuthContext);
    const [comments, setComments] = useState([]);
    const [newComment, setNewComment] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [loadingComments, setLoadingComments] = useState(true);

    useEffect(() => {
        fetchComments();
    }, []);

    const fetchComments = async () => {
        try {
            const response = await client.get(`/comentarios/${news.id}`);
            setComments(response.data);
        } catch (error) {
            console.error('Error fetching comments:', error);
        } finally {
            setLoadingComments(false);
        }
    };

    const handleSendComment = async () => {
        if (!newComment.trim()) return;
        setSubmitting(true);
        try {
            await client.post('/comentarios', { id_noticia: news.id, texto: newComment });
            Alert.alert('Enviado', 'Tu comentario aparecerá una vez que sea revisado por un administrador');
            setNewComment('');
        } catch (error) {
            Alert.alert('Error', 'No se pudo enviar el comentario');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <ScrollView style={styles.container}>
            <Image source={{ uri: news.imagen_url }} style={styles.image} />
            <View style={styles.content}>
                <Text style={styles.title}>{news.titulo}</Text>
                <Text style={styles.date}>{new Date(news.fecha_publicacion).toLocaleDateString()}</Text>
                <Text style={styles.body}>{news.contenido}</Text>
            </View>

            <View style={styles.commentsSection}>
                <Text style={styles.commentsHeader}>Comentarios</Text>
                
                {loadingComments ? (
                    <ActivityIndicator size="small" color="#1B3C53" />
                ) : comments.length > 0 ? (
                    comments.map(c => (
                        <View key={c.id} style={styles.commentCard}>
                            <Text style={styles.commentUser}>{c.usuario_nombre}</Text>
                            <Text style={styles.commentText}>{c.texto}</Text>
                        </View>
                    ))
                ) : (
                    <Text style={styles.noComments}>No hay comentarios aún.</Text>
                )}

                {user ? (
                    <View style={styles.form}>
                        <TextInput
                            style={styles.input}
                            placeholder="Escribe un comentario..."
                            value={newComment}
                            onChangeText={setNewComment}
                            multiline
                        />
                        <TouchableOpacity 
                            style={[styles.button, submitting && { opacity: 0.7 }]} 
                            onPress={handleSendComment}
                            disabled={submitting}
                        >
                            <Text style={styles.buttonText}>{submitting ? 'Enviando...' : 'Comentar'}</Text>
                        </TouchableOpacity>
                        <Text style={styles.notice}>
                            Tu comentario aparecerá una vez que sea revisado por un administrador.
                        </Text>
                    </View>
                ) : (
                    <View style={styles.loginNotice}>
                        <Text style={styles.loginNoticeText}>Debes iniciar sesión para comentar.</Text>
                    </View>
                )}
            </View>
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#FFF' },
    image: { width: '100%', height: 250 },
    content: { padding: 20 },
    title: { fontSize: 24, fontWeight: 'bold', color: '#1B3C53', marginBottom: 10 },
    date: { fontSize: 14, color: '#666', marginBottom: 20 },
    body: { fontSize: 16, lineHeight: 24, color: '#333' },
    commentsSection: { padding: 20, backgroundColor: '#F9F9F9', borderTopWidth: 1, borderTopColor: '#EEE' },
    commentsHeader: { fontSize: 20, fontWeight: 'bold', color: '#1B3C53', marginBottom: 15 },
    commentCard: { backgroundColor: '#FFF', padding: 12, borderRadius: 8, marginBottom: 10, borderWidth: 1, borderColor: '#EEE' },
    commentUser: { fontWeight: 'bold', fontSize: 14, color: '#1B3C53', marginBottom: 4 },
    commentText: { fontSize: 14, color: '#444' },
    noComments: { fontStyle: 'italic', color: '#888', textAlign: 'center', marginBottom: 15 },
    form: { marginTop: 20, borderTopWidth: 1, borderTopColor: '#DDD', paddingTop: 20 },
    input: { backgroundColor: '#FFF', borderWidth: 1, borderColor: '#CCC', borderRadius: 8, padding: 12, height: 80, textAlignVertical: 'top', marginBottom: 10 },
    button: { backgroundColor: '#1B3C53', padding: 12, borderRadius: 8, alignItems: 'center' },
    buttonText: { color: '#FFF', fontWeight: 'bold' },
    notice: { fontSize: 11, color: '#666', marginTop: 10, textAlign: 'center' },
    loginNotice: { backgroundColor: '#EEE', padding: 15, borderRadius: 8, marginTop: 10, alignItems: 'center' },
    loginNoticeText: { color: '#666', fontSize: 14 }
});

export default NewsDetailScreen;
