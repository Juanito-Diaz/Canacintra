import React, { useState, useEffect, useContext } from 'react';
import { View, Text, StyleSheet, FlatList, Image, TouchableOpacity, Dimensions, ScrollView, ActivityIndicator } from 'react-native';
import client from '../api/client';
import { AuthContext } from '../context/AuthContext';

const { width } = Dimensions.get('window');

const HomeScreen = ({ navigation }) => {
    const { user, logout } = useContext(AuthContext);
    const [recentNews, setRecentNews] = useState([]);
    const [allNews, setAllNews] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeSlide, setActiveSlide] = useState(0);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [recentRes, allRes] = await Promise.all([
                client.get('/noticias/recientes'),
                client.get('/noticias')
            ]);
            setRecentNews(recentRes.data);
            setAllNews(allRes.data);
        } catch (error) {
            console.error('Error fetching news:', error);
        } finally {
            setLoading(false);
        }
    };

    const renderCarouselItem = ({ item }) => (
        <TouchableOpacity 
            style={styles.carouselItem}
            onPress={() => navigation.navigate('NewsDetail', { news: item })}
        >
            <Image source={{ uri: item.imagen_url }} style={styles.carouselImage} />
            <View style={styles.carouselTextContainer}>
                <Text style={styles.carouselTitle} numberOfLines={2}>{item.titulo}</Text>
            </View>
        </TouchableOpacity>
    );

    const renderNewsItem = ({ item }) => (
        <TouchableOpacity 
            style={styles.newsCard}
            onPress={() => navigation.navigate('NewsDetail', { news: item })}
        >
            <Image source={{ uri: item.imagen_url }} style={styles.newsImage} />
            <View style={styles.newsInfo}>
                <Text style={styles.newsTitle}>{item.titulo}</Text>
                <Text style={styles.newsDate}>{new Date(item.fecha_publicacion).toLocaleDateString()}</Text>
            </View>
        </TouchableOpacity>
    );

    if (loading) return <ActivityIndicator size="large" color="#1B3C53" style={{ flex: 1 }} />;

    return (
        <ScrollView style={styles.container}>
            {/* Header / Auth State */}
            <View style={styles.header}>
                <Text style={styles.headerBrand}>CANACINTRA</Text>
                {user ? (
                    <View style={styles.userSection}>
                        <Text style={styles.userName}>Hola, {user.nombre}</Text>
                        <TouchableOpacity onPress={logout}><Text style={styles.logoutText}>Salir</Text></TouchableOpacity>
                        {user.rol === 'admin' && (
                            <TouchableOpacity 
                                style={styles.adminButton}
                                onPress={() => navigation.navigate('AdminModeration')}
                            >
                                <Text style={styles.adminButtonText}>Moderación</Text>
                            </TouchableOpacity>
                        )}
                    </View>
                ) : (
                    <TouchableOpacity onPress={() => navigation.navigate('Login')}>
                        <Text style={styles.loginLink}>Iniciar Sesión</Text>
                    </TouchableOpacity>
                )}
            </View>

            {/* Carousel */}
            <View style={styles.carouselContainer}>
                <FlatList
                    data={recentNews}
                    renderItem={renderCarouselItem}
                    horizontal
                    pagingEnabled
                    showsHorizontalScrollIndicator={false}
                    onScroll={(e) => {
                        const slide = Math.ceil(e.nativeEvent.contentOffset.x / e.nativeEvent.layoutMeasurement.width);
                        if (slide !== activeSlide) setActiveSlide(slide);
                    }}
                    keyExtractor={(item) => item.id.toString()}
                />
                <View style={styles.pagination}>
                    {recentNews.map((_, i) => (
                        <View key={i} style={[styles.dot, activeSlide === i ? styles.activeDot : null]} />
                    ))}
                </View>
            </View>

            {/* All News List */}
            <View style={styles.listSection}>
                <Text style={styles.sectionTitle}>Últimas Noticias</Text>
                {allNews.map((item) => (
                    <View key={item.id}>{renderNewsItem({ item })}</View>
                ))}
            </View>
        </ScrollView>
    );
};

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#F5F5F5' },
    header: { padding: 20, paddingTop: 50, backgroundColor: '#1B3C53', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
    headerBrand: { color: '#FFF', fontSize: 20, fontWeight: 'bold' },
    loginLink: { color: '#FFF', fontWeight: 'bold' },
    userSection: { alignItems: 'flex-end' },
    userName: { color: '#FFF', fontSize: 12 },
    logoutText: { color: '#D2C1B6', fontSize: 10, marginTop: 2 },
    adminButton: { backgroundColor: '#456882', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 4, marginTop: 5 },
    adminButtonText: { color: '#FFF', fontSize: 10, fontWeight: 'bold' },
    carouselContainer: { height: 250 },
    carouselItem: { width, height: 250 },
    carouselImage: { width: '100%', height: '100%' },
    carouselTextContainer: { position: 'absolute', bottom: 0, left: 0, right: 0, backgroundColor: 'rgba(0,0,0,0.5)', padding: 15 },
    carouselTitle: { color: '#FFF', fontSize: 18, fontWeight: 'bold' },
    pagination: { flexDirection: 'row', position: 'absolute', bottom: 10, alignSelf: 'center' },
    dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: 'rgba(255,255,255,0.4)', marginHorizontal: 4 },
    activeDot: { backgroundColor: '#FFF' },
    listSection: { padding: 15 },
    sectionTitle: { fontSize: 20, fontWeight: 'bold', color: '#1B3C53', marginBottom: 15 },
    newsCard: { backgroundColor: '#FFF', borderRadius: 10, marginBottom: 15, overflow: 'hidden', elevation: 3, flexDirection: 'row' },
    newsImage: { width: 100, height: 100 },
    newsInfo: { padding: 10, flex: 1, justifyContent: 'center' },
    newsTitle: { fontSize: 14, fontWeight: 'bold', color: '#333' },
    newsDate: { fontSize: 12, color: '#666', marginTop: 5 },
});

export default HomeScreen;
