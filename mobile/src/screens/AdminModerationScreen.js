import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import client from '../api/client';

const AdminModerationScreen = () => {
    const [pendingComments, setPendingComments] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchPending();
    }, []);

    const fetchPending = async () => {
        try {
            const response = await client.get('/admin/comentarios/pendientes');
            setPendingComments(response.data);
        } catch (error) {
            console.error('Error fetching pending comments:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleApprove = async (id) => {
        try {
            await client.patch(`/comentarios/aprobar/${id}`);
            setPendingComments(prev => prev.filter(c => c.id !== id));
            Alert.alert('Éxito', 'Comentario aprobado');
        } catch (error) {
            Alert.alert('Error', 'No se pudo aprobar');
        }
    };

    const handleDelete = async (id) => {
        try {
            await client.delete(`/comentarios/${id}`);
            setPendingComments(prev => prev.filter(c => c.id !== id));
            Alert.alert('Éxito', 'Comentario eliminado');
        } catch (error) {
            Alert.alert('Error', 'No se pudo eliminar');
        }
    };

    const renderItem = ({ item }) => (
        <View style={styles.card}>
            <View style={styles.info}>
                <Text style={styles.user}>{item.usuario_nombre}</Text>
                <Text style={styles.noticia}>En: {item.noticia_titulo}</Text>
                <Text style={styles.text}>{item.texto}</Text>
                <Text style={styles.date}>{new Date(item.fecha_creacion).toLocaleString()}</Text>
            </View>
            <View style={styles.actions}>
                <TouchableOpacity style={styles.approveBtn} onPress={() => handleApprove(item.id)}>
                    <Text style={styles.btnText}>Aprobar</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.deleteBtn} onPress={() => handleDelete(item.id)}>
                    <Text style={styles.btnText}>Eliminar</Text>
                </TouchableOpacity>
            </View>
        </View>
    );

    return (
        <View style={styles.container}>
            <Text style={styles.title}>Moderación de Comentarios</Text>
            {loading ? (
                <ActivityIndicator size="large" color="#1B3C53" />
            ) : pendingComments.length > 0 ? (
                <FlatList
                    data={pendingComments}
                    renderItem={renderItem}
                    keyExtractor={item => item.id.toString()}
                    contentContainerStyle={styles.list}
                />
            ) : (
                <Text style={styles.empty}>No hay comentarios pendientes.</Text>
            )}
        </View>
    );
};

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#F5F5F5', padding: 20 },
    title: { fontSize: 22, fontWeight: 'bold', color: '#1B3C53', marginBottom: 20 },
    list: { paddingBottom: 20 },
    card: { backgroundColor: '#FFF', borderRadius: 10, padding: 15, marginBottom: 15, elevation: 3 },
    info: { marginBottom: 15 },
    user: { fontWeight: 'bold', fontSize: 16, color: '#1B3C53' },
    noticia: { fontSize: 12, color: '#666', fontStyle: 'italic', marginBottom: 5 },
    text: { fontSize: 14, color: '#444' },
    date: { fontSize: 11, color: '#999', marginTop: 5 },
    actions: { flexDirection: 'row', justifyContent: 'flex-end' },
    approveBtn: { backgroundColor: '#2E7D32', paddingHorizontal: 15, paddingVertical: 8, borderRadius: 5, marginLeft: 10 },
    deleteBtn: { backgroundColor: '#C62828', paddingHorizontal: 15, paddingVertical: 8, borderRadius: 5, marginLeft: 10 },
    btnText: { color: '#FFF', fontWeight: 'bold', fontSize: 12 },
    empty: { textAlign: 'center', marginTop: 50, color: '#888', fontStyle: 'italic' }
});

export default AdminModerationScreen;
